"""FastAPI entrypoint: wires the deterministic envelope around the agent core.

  ticket -> PRE-FLIGHT (sensitivity) -> AGENT CORE (Claude loop) -> POST-FLIGHT
            (validate citations + compute confidence + enforce escalate) -> response
"""
from fastapi import FastAPI

from app.agent import run_agent
from app.guardrail import compute_confidence, scan_sensitivity
from app.schemas import Citation, QueryRequest, QueryResponse

app = FastAPI(title="Support Deflector", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    # 1) PRE-FLIGHT — deterministic. Sensitive data never reaches the model.
    sensitive, _detail = scan_sensitivity(req.question)
    if sensitive:
        return QueryResponse(escalate=True, escalation_reason="sensitive_data")

    # 2) AGENT CORE — model decides how to search and whether it can answer.
    result = run_agent(req.question, req.category)

    if result["kind"] == "escalate":
        return QueryResponse(escalate=True, escalation_reason="out_of_scope")

    # 3) POST-FLIGHT — deterministic. Validate citations, compute confidence in code,
    #    and force escalation on Low. The model cannot self-declare confidence.
    data = result["input"]
    seen = result["seen_chunks"]
    valid = [cid for cid in data.get("cited_chunk_ids", []) if cid in seen]
    cited_scores = [seen[cid]["score"] for cid in valid]

    confidence = compute_confidence(cited_scores, bool(data.get("is_fully_grounded")))
    if confidence == "Low":
        return QueryResponse(escalate=True, escalation_reason="low_confidence")

    citations = [Citation(chunk_id=cid, doc=seen[cid]["doc"], score=seen[cid]["score"]) for cid in valid]
    return QueryResponse(
        answer=data["answer"],
        citations=citations,
        confidence=confidence,
        escalate=False,
    )
