"""Serving-layer Dagster asset: index redacted bronze documents into Qdrant."""

from __future__ import annotations

import polars as pl
from dagster import asset

from pipelines.config import BRONZE_DIR


@asset(group_name="serving", deps=["bronze_documents"])
def vector_index(context) -> None:
    """Embed redacted document text into the Qdrant collection (RAG-ready)."""
    from serving.vector_store import index_documents

    bronze = pl.read_delta(str(BRONZE_DIR))
    records = [
        {"source_sha256": r["source_sha256"], "text": r["text"]}
        for r in bronze.iter_rows(named=True)
        if r["text"]
    ]
    stats = index_documents(records)
    context.add_output_metadata(stats)
