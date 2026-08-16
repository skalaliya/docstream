"""Qdrant loader: redacted document text -> embeddings -> vector collection."""

from __future__ import annotations

import os
import uuid

from quality.redaction import redact
from serving.embeddings import get_embedder

COLLECTION = "docstream_documents"
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")


def index_documents(records: list[dict]) -> dict:
    """Redact, embed and upsert document records into Qdrant.

    Each record needs ``source_sha256`` and ``text``. Returns indexing stats.
    """
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    embedder = get_embedder()
    client = QdrantClient(url=QDRANT_URL)

    if not client.collection_exists(COLLECTION):
        client.create_collection(
            COLLECTION,
            vectors_config=VectorParams(size=embedder.dim, distance=Distance.COSINE),
        )

    redacted, total_redactions = [], 0
    for r in records:
        report = redact(r["text"])
        total_redactions += report.total_redactions
        redacted.append({**r, "text": report.text})

    vectors = embedder.embed([r["text"] for r in redacted])
    points = [
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, r["source_sha256"])),  # idempotent ids
            vector=v,
            payload={"source_sha256": r["source_sha256"], "text": r["text"][:2000]},
        )
        for r, v in zip(redacted, vectors)
    ]
    client.upsert(COLLECTION, points)

    return {
        "indexed": len(points),
        "pii_redactions": total_redactions,
        "embedder": embedder.name,
    }


def search(query: str, limit: int = 5) -> list[dict]:
    """Semantic search over indexed documents."""
    from qdrant_client import QdrantClient

    embedder = get_embedder()
    client = QdrantClient(url=QDRANT_URL)
    hits = client.query_points(
        COLLECTION, query=embedder.embed([query])[0], limit=limit
    ).points
    return [{"score": h.score, **(h.payload or {})} for h in hits]
