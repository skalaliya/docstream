"""Tests for silver parsing and validation gates."""

import polars as pl

from pipelines.parsing import parse_invoice_text
from quality.schemas import validate_silver

SAMPLE = """
ACME Supplies Pty Ltd
ABN: 51 824 753 556
Invoice No: INV-2026-0042
Date: 12 Mar 2026
Total Amount Due: $1,234.56 AUD
"""


def test_parse_full_invoice():
    p = parse_invoice_text(SAMPLE)
    assert p.invoice_number == "INV-2026-0042"
    assert p.invoice_date == "2026-03-12"
    assert p.vendor_abn == "51824753556"
    assert p.total_amount == 1234.56
    assert p.currency == "AUD"


def test_parse_iso_and_slash_dates():
    assert parse_invoice_text("Date: 2026-01-05").invoice_date == "2026-01-05"
    assert parse_invoice_text("Date: 5/1/2026").invoice_date == "2026-01-05"


def test_parse_missing_fields_are_none():
    p = parse_invoice_text("just some random text")
    assert p.invoice_number is None
    assert p.total_amount is None


def _row(**overrides) -> dict:
    base = {
        "source_sha256": "a" * 64,
        "invoice_number": "INV-1",
        "invoice_date": "2026-03-12",
        "vendor_abn": "51824753556",
        "total_amount": 100.0,
        "currency": "AUD",
    }
    return {**base, **overrides}


def test_validate_splits_valid_and_quarantine():
    df = pl.DataFrame([_row(), _row(source_sha256="b" * 64, invoice_number=None)])
    valid, quarantined = validate_silver(df)
    assert valid.height == 1
    assert quarantined.height == 1
    assert "quarantine_reason" in quarantined.columns


def test_validate_rejects_nonpositive_total():
    df = pl.DataFrame([_row(total_amount=0.0)])
    valid, quarantined = validate_silver(df)
    assert valid.height == 0
    assert quarantined.height == 1
