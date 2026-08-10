"""Agent core: a hand-written Claude tool loop (legible on purpose).

The model drives retrieval and decides when to answer or escalate. It ends the
loop by calling ONE of two terminal tools:
  - submit_answer(answer, cited_chunk_ids, is_fully_grounded)
  - escalate(reason, summary)
The only non-terminal tool is search_knowledge_base, which it may call repeatedly
(reformulating the query) — the one reason this is an agent, not one-shot RAG.
"""
import json

import anthropic

from app.config import settings
from app.rag import search_knowledge_base

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are a customer-support deflection agent for a B2B SaaS product.
Answer ONLY from content returned by the search_knowledge_base tool. Never use outside knowledge.

Workflow:
1. Call search_knowledge_base with a focused query. If results look weak or off-topic,
   reformulate and search again (you may search a few times).
2. If the knowledge base clearly answers the question, call submit_answer with the answer,
   the chunk_ids you actually used, and is_fully_grounded=true only if every claim is
   supported by those chunks.
3. If the knowledge base does not cover the question, call escalate with reason "out_of_scope".

Always finish by calling either submit_answer or escalate. Keep answers concise and factual.
Format the answer in Markdown: use a numbered list with ONE step per line for procedures,
and **bold** for UI labels and button names."""

TOOLS = [
    {
        "name": "search_knowledge_base",
        "description": "Search the support knowledge base. Returns chunks with chunk_id, doc, text, score.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (reformulate if needed)."},
                "category": {
                    "type": "string",
                    "enum": ["billing", "api", "integrations", "authentication", "account", "data"],
                    "description": "Optional category filter to narrow the search.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "submit_answer",
        "description": "Provide the final answer grounded in retrieved chunks. Terminal.",
        "input_schema": {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "cited_chunk_ids": {"type": "array", "items": {"type": "string"}},
                "is_fully_grounded": {"type": "boolean"},
            },
            "required": ["answer", "cited_chunk_ids", "is_fully_grounded"],
        },
    },
    {
        "name": "escalate",
        "description": "Escalate to a human when the KB can't answer. Terminal.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "enum": ["out_of_scope"]},
                "summary": {"type": "string"},
            },
            "required": ["reason", "summary"],
        },
    },
]

TERMINAL = {"submit_answer", "escalate"}


def agent_stream(question: str, category: str | None = None):
    """Generator that yields trace events as the agent works, and *returns* the final
    terminal decision (captured via StopIteration.value). Events:
      {type: "search", n, query, category, hits: [{chunk_id, doc, score, text}]}
      {type: "decision", kind: "submit_answer" | "escalate", reason?}
    """
    messages = [{"role": "user", "content": question if not category
                 else f"[category hint: {category}]\n{question}"}]
    seen_chunks: dict[str, dict] = {}  # chunk_id -> chunk (accumulated across searches)
    search_n = 0

    for _ in range(settings.max_agent_iters):
        resp = _client.messages.create(
            model=settings.gen_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        if not tool_uses:
            break  # model replied with text instead of a tool -> fail-safe escalate below

        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for tu in tool_uses:
            if tu.name in TERMINAL:
                yield {"type": "decision", "kind": tu.name,
                       "reason": tu.input.get("reason") if tu.name == "escalate" else None}
                return {"kind": tu.name, "input": tu.input, "seen_chunks": seen_chunks}
            if tu.name == "search_knowledge_base":
                search_n += 1
                chunks = search_knowledge_base(tu.input["query"], tu.input.get("category"))
                for c in chunks:
                    seen_chunks[c["chunk_id"]] = c
                yield {
                    "type": "search",
                    "n": search_n,
                    "query": tu.input["query"],
                    "category": tu.input.get("category"),
                    "hits": [
                        {"chunk_id": c["chunk_id"], "doc": c["doc"],
                         "score": round(c["score"], 3), "text": c["text"]}
                        for c in chunks
                    ],
                }
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(chunks),
                })
        messages.append({"role": "user", "content": tool_results})

    # Fail-safe: never reached a terminal tool -> escalate.
    yield {"type": "decision", "kind": "escalate", "reason": "out_of_scope"}
    return {"kind": "escalate",
            "input": {"reason": "out_of_scope", "summary": "Agent did not reach a confident answer."},
            "seen_chunks": seen_chunks}


def run_agent(question: str, category: str | None = None) -> dict:
    """Non-streaming: drain the generator, return the terminal decision."""
    gen = agent_stream(question, category)
    while True:
        try:
            next(gen)
        except StopIteration as e:
            return e.value
