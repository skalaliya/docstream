"""Silver-layer Dagster assets: parse bronze text, validate, quarantine."""

from __future__ import annotations

import polars as pl
from dagster import MetadataValue, asset

from pipelines.config import BRONZE_DIR, DATA_DIR
from pipelines.parsing import parse_invoice_text
from quality.schemas import validate_silver

SILVER_DIR = DATA_DIR / "silver"
QUARANTINE_DIR = DATA_DIR / "quarantine"


@asset(group_name="silver", deps=["bronze_documents"])
def silver_invoices(context) -> None:
    """Parse bronze text into typed invoice records; gate with Pandera; quarantine failures."""
    bronze = pl.read_delta(str(BRONZE_DIR))

    parsed = pl.DataFrame(
        [
            {"source_sha256": row["source_sha256"], **parse_invoice_text(row["text"]).to_record()}
            for row in bronze.iter_rows(named=True)
        ]
    )

    valid, quarantined = validate_silver(parsed)

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    valid.write_parquet(SILVER_DIR / "invoices.parquet")
    if quarantined.height:
        quarantined.write_parquet(QUARANTINE_DIR / "invoices_quarantine.parquet")

    context.add_output_metadata(
        {
            "valid_rows": valid.height,
            "quarantined_rows": quarantined.height,
            "pass_rate": MetadataValue.float(
                round(valid.height / max(parsed.height, 1), 3)
            ),
        }
    )
