"""Data layer: OpenAI embeddings + Pinecone retrieval.

`search_knowledge_base` is the abstraction seam — swap Pinecone for pgvector/
another store here and nothing else in the app changes.
"""
from functools import lru_cache
from openai import OpenAI
from pinecone import Pinecone

from app.config import settings

_openai = OpenAI(api_key=settings.openai_api_key)


@lru_cache(maxsize=1)
def _index():
    pc = Pinecone(api_key=settings.pinecone_api_key)
    return pc.Index(settings.pinecone_index)


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts with OpenAI, sized to EMBED_DIM (must match the index).

    text-embedding-3-* supports the `dimensions` param, so we can match whatever
    dimension the Pinecone index was created with (e.g. 1024 or the native 1536).
    """
    resp = _openai.embeddings.create(
        model=settings.embed_model, input=texts, dimensions=settings.embed_dim
    )
    return [d.embedding for d in resp.data]


def search_knowledge_base(query: str, category: str | None = None, top_k: int | None = None) -> list[dict]:
    """Retrieve the most relevant chunks. Returns [{chunk_id, doc, category, text, score}]."""
    top_k = top_k or settings.top_k
    vector = embed([query])[0]
    flt = {"category": category} if category else None
    res = _index().query(vector=vector, top_k=top_k, include_metadata=True, filter=flt)
    out = []
    for m in res.get("matches", []):
        md = m.get("metadata", {}) or {}
        out.append(
            {
                "chunk_id": m["id"],
                "doc": md.get("doc", ""),
                "category": md.get("category", ""),
                "text": md.get("text", ""),
                "score": float(m.get("score", 0.0)),
            }
        )
    return out
