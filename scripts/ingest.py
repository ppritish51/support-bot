"""One-time ingestion: docs/<category>/*.md -> chunk by Q&A -> OpenAI embed -> Pinecone.

Run once before serving:  python -m scripts.ingest
Layout: each subfolder of docs/ is a CATEGORY (billing, api, integrations, ...),
each .md file is a document. Chunk strategy: split each file on `## ` headings so
one chunk = one Q&A pair (FAQs are already semantically chunked).
"""
import os
import re
import time

from pinecone import Pinecone, ServerlessSpec

from app.config import settings
from app.rag import embed

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")


def chunk_file(path: str, category: str) -> list[dict]:
    """Return [{chunk_id, doc, category, text}] split on '## ' headings."""
    stem = os.path.splitext(os.path.basename(path))[0]
    doc = f"{category}/{os.path.basename(path)}"
    raw = open(path, encoding="utf-8").read()
    # Split keeping headings; drop any preamble before the first '## '.
    parts = re.split(r"(?m)^##\s+", raw)
    chunks = []
    for i, part in enumerate(p for p in parts[1:] if p.strip()):
        text = "## " + part.strip()
        chunks.append({
            "chunk_id": f"{category}/{stem}#{i}",  # unique across all files
            "doc": doc,
            "category": category,
            "text": text,
        })
    return chunks


def collect_chunks() -> list[dict]:
    """Walk docs/<category>/*.md and chunk every file."""
    chunks: list[dict] = []
    for root, _dirs, files in os.walk(DOCS_DIR):
        if root == DOCS_DIR:
            continue  # categories live in subfolders
        category = os.path.basename(root)
        for name in sorted(files):
            if name.endswith(".md"):
                chunks.extend(chunk_file(os.path.join(root, name), category))
    return chunks


def ensure_index(pc: Pinecone) -> None:
    name = settings.pinecone_index
    existing = [ix["name"] for ix in pc.list_indexes()]
    if name in existing:
        # Fail loudly on a dimension mismatch instead of at upsert time.
        desc = pc.describe_index(name)
        dim = getattr(desc, "dimension", None) or desc["dimension"]
        if dim != settings.embed_dim:
            raise SystemExit(
                f"Index '{name}' has dimension {dim}, but EMBED_DIM={settings.embed_dim}.\n"
                f"Fix: set EMBED_DIM={dim} in .env to match the index, "
                f"or delete the index to recreate it at {settings.embed_dim}."
            )
        return
    print(f"Creating index '{name}' (dim={settings.embed_dim})...")
    pc.create_index(
        name=name,
        dimension=settings.embed_dim,
        metric="cosine",
        spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
    )
    while not pc.describe_index(name)["status"]["ready"]:
        time.sleep(1)


def main() -> None:
    chunks = collect_chunks()
    if not chunks:
        raise SystemExit(f"No .md files under {DOCS_DIR}/<category>/")
    docs = {c["doc"] for c in chunks}
    cats = {c["category"] for c in chunks}
    print(f"{len(chunks)} chunks from {len(docs)} docs across {len(cats)} categories: {sorted(cats)}")

    pc = Pinecone(api_key=settings.pinecone_api_key)
    ensure_index(pc)
    index = pc.Index(settings.pinecone_index)

    vectors = embed([c["text"] for c in chunks])
    records = [
        {
            "id": c["chunk_id"],
            "values": v,
            "metadata": {"doc": c["doc"], "category": c["category"], "text": c["text"]},
        }
        for c, v in zip(chunks, vectors)
    ]
    index.upsert(vectors=records)
    print(f"Upserted {len(records)} vectors into '{settings.pinecone_index}'.")


if __name__ == "__main__":
    main()
