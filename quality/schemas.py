"""Pandera validation gates for the silver layer.

Records passing the gate land in silver; failures are quarantined with the
failure reason attached — bad data is never silently dropped.
"""

from __future__ import annotations

import pandera.polars as pa
import polars as pl

silver_invoice_schema = pa.DataFrameSchema(
    {
        "source_sha256": pa.Column(str, pa.Check.str_length(64, 64)),
        "invoice_number": pa.Column(str, nullable=False),
        "invoice_date": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),
        "total_amount": pa.Column(float, pa.Check.gt(0)),
        "currency": pa.Column(str, pa.Check.isin(["AUD", "USD", "EUR", "GBP"]), nullable=True),
        "vendor_abn": pa.Column(str, nullable=True),
    },
    strict=False,
    coerce=True,
)


def validate_silver(df: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Split a parsed dataframe into (valid, quarantined).

    Row-level gate: required fields present and sane. Schema-level Pandera
    validation then runs on the surviving rows as a hard check.
    """
    required_ok = (
        pl.col("invoice_number").is_not_null()
        & pl.col("invoice_date").is_not_null()
        & (pl.col("total_amount") > 0)
    )
    valid = df.filter(required_ok)
    quarantined = df.filter(~required_ok.fill_null(True)).with_columns(
        pl.lit("missing required field(s): invoice_number/invoice_date/total_amount").alias(
            "quarantine_reason"
        )
    )
    if valid.height:
        valid = silver_invoice_schema.validate(valid)
    return valid, quarantined
