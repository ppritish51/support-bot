"""FastAPI entrypoint: the deterministic envelope + a streaming glass-box console.

  ticket -> PRE-FLIGHT (sensitivity) -> AGENT CORE (Claude loop) -> POST-FLIGHT
            (validate citations + compute confidence + enforce escalate) -> response

Endpoints:
  GET  /               glass-box console (Jinja)
  POST /query          JSON API (non-streaming)
  GET  /query/stream   Server-Sent Events: live trace + final result
  GET  /stats          session deflection stats
  GET  /health
"""
import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.agent import agent_stream, run_agent
from app.guardrail import compute_confidence, scan_sensitivity
from app.schemas import Citation, QueryRequest, QueryResponse

app = FastAPI(title="Support Deflector", version="0.2.0")
templates = Jinja2Templates(directory="templates")

# In-memory session stats (fine for a demo; a real system would persist these).
_stats = {"resolved": 0, "escalated": 0}


def _stats_view() -> dict:
    total = _stats["resolved"] + _stats["escalated"]
    pct = round(100 * _stats["resolved"] / total, 1) if total else 0.0
    return {"resolved": _stats["resolved"], "escalated": _stats["escalated"],
            "total": total, "deflection_pct": pct}


def _finalize(result: dict) -> dict:
    """POST-FLIGHT: validate citations, compute confidence in code, enforce escalate-on-Low.
    Also records session stats. Returns a plain dict (shared by JSON + SSE paths)."""
    data, seen = result["input"], result["seen_chunks"]

    if result["kind"] == "escalate":
        _stats["escalated"] += 1
        return {"answer": None, "citations": [], "confidence": None,
                "escalate": True, "escalation_reason": "out_of_scope",
                "escalation_detail": data.get("reason")}

    valid = [cid for cid in data.get("cited_chunk_ids", []) if cid in seen]
    scores = [seen[cid]["score"] for cid in valid]
    confidence = compute_confidence(scores, bool(data.get("is_fully_grounded")))

    if confidence == "Low":
        _stats["escalated"] += 1
        return {"answer": None, "citations": [], "confidence": "Low",
                "escalate": True, "escalation_reason": "low_confidence", "escalation_detail": None}

    _stats["resolved"] += 1
    citations = [
        {"chunk_id": cid, "doc": seen[cid]["doc"],
         "score": round(seen[cid]["score"], 3), "text": seen[cid]["text"]}
        for cid in valid
    ]
    return {"answer": data["answer"], "citations": citations, "confidence": confidence,
            "escalate": False, "escalation_reason": None, "escalation_detail": None}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/stats")
def stats() -> dict:
    return _stats_view()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Starlette >=0.29 signature: request first, then template name.
    return templates.TemplateResponse(request, "index.html")


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    sensitive, _detail = scan_sensitivity(req.question)
    if sensitive:
        _stats["escalated"] += 1
        return QueryResponse(escalate=True, escalation_reason="sensitive_data")

    f = _finalize(run_agent(req.question, req.category))
    return QueryResponse(
        answer=f["answer"],
        citations=[Citation(**c) for c in f["citations"]],
        confidence=f["confidence"],
        escalate=f["escalate"],
        escalation_reason=f["escalation_reason"],
    )


@app.get("/query/stream")
def query_stream(question: str, category: str | None = None):
    """SSE: emit pre-flight, each search step, the decision, then the final result."""

    def sse(obj: dict) -> str:
        return f"data: {json.dumps(obj)}\n\n"

    def gen():
        sensitive, detail = scan_sensitivity(question)
        yield sse({"type": "preflight", "sensitive": sensitive, "detail": detail})

        if sensitive:
            _stats["escalated"] += 1
            yield sse({"type": "result", "answer": None, "citations": [], "confidence": None,
                       "escalate": True, "escalation_reason": "sensitive_data",
                       "escalation_detail": detail, "stats": _stats_view()})
            yield sse({"type": "done"})
            return

        agen = agent_stream(question, category)
        result = None
        while True:
            try:
                yield sse(next(agen))
            except StopIteration as e:
                result = e.value
                break

        final = _finalize(result)
        final["type"] = "result"
        final["stats"] = _stats_view()
        yield sse(final)
        yield sse({"type": "done"})

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
