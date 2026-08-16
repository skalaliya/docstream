"""Dagster assets: landing -> extraction -> bronze Delta table."""

from __future__ import annotations

from pathlib import Path

import polars as pl
from dagster import MetadataValue, asset

from pipelines.config import BRONZE_DIR, LANDING_DIR, SUPPORTED_EXTENSIONS
from pipelines.extraction import ExtractionResult, get_extractor


@asset(group_name="ingestion")
def landing_files() -> list[Path]:
    """Discover new documents in the landing zone."""
    LANDING_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(
        p for p in LANDING_DIR.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return files


@asset(group_name="ingestion")
def extracted_documents(landing_files: list[Path]) -> list[ExtractionResult]:
    """Run OCR/text extraction over landed files."""
    extractor = get_extractor()
    return [extractor.extract(p) for p in landing_files]


@asset(group_name="bronze")
def bronze_documents(context, extracted_documents: list[ExtractionResult]) -> None:
    """Append extraction results to the bronze Delta table (idempotent via sha256 dedupe)."""
    if not extracted_documents:
        context.log.info("No new documents to write.")
        return

    df = pl.DataFrame([r.to_record() for r in extracted_documents])

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        existing = pl.read_delta(str(BRONZE_DIR))
        seen = set(existing["source_sha256"].to_list())
        df = df.filter(~pl.col("source_sha256").is_in(seen))
        mode = "append"
    except Exception:
        mode = "overwrite"  # first write

    if df.height:
        df.write_delta(str(BRONZE_DIR), mode=mode)

    context.add_output_metadata(
        {
            "rows_written": df.height,
            "preview": MetadataValue.md(df.head(5).to_pandas().to_markdown() if df.height else "none"),
        }
    )
