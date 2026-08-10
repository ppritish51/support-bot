"""Smoke eval: 5 tickets exercising High / Medium / Low / sensitive / out-of-scope.

Run after ingestion + env are set:  python eval.py
Calls the full pipeline (pre-flight -> agent -> post-flight) in-process.
"""
from app.main import query
from app.schemas import QueryRequest

CASES = [
    ("How do I update the credit card on my account?", None, "expect: High, billing"),
    ("your API keeps throwing 429 when I hit it a lot, how do I fix it?", None,
     "expect: High/Medium, api_limits (needs reformulation)"),
    ("I need a refund to my card 4111 1111 1111 1111", None,
     "expect: ESCALATE sensitive_data (PII + refund)"),
    ("Does your product integrate with Salesforce?", None,
     "expect: ESCALATE out_of_scope"),
    ("How often should I rotate my webhook signing secret for compliance?", None,
     "expect: Low/escalate — KB has secret location, not rotation policy"),
]


def main() -> None:
    for i, (q, cat, note) in enumerate(CASES, 1):
        r = query(QueryRequest(question=q, category=cat))
        print(f"\n[{i}] {q}\n    {note}")
        if r.escalate:
            print(f"    -> ESCALATE ({r.escalation_reason})")
        else:
            cites = ", ".join(f"{c.chunk_id}({c.score:.2f})" for c in r.citations)
            print(f"    -> {r.confidence} | cites: {cites}")
            print(f"    answer: {r.answer[:160]}{'...' if r.answer and len(r.answer) > 160 else ''}")


if __name__ == "__main__":
    main()
