"""Silver-layer parsing: turn raw extracted text into structured invoice fields.

Deliberately conservative: regex heuristics with explicit confidence flags.
A field the parser can't find is ``None`` — never guessed. Downstream Pandera
gates decide whether a record is silver-worthy or quarantined.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "ymd"),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"), "dmy"),
    (re.compile(r"\b(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{4})\b", re.IGNORECASE), "dMy"),
]

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
)}

TOTAL_RE = re.compile(
    r"(?:total|amount due|balance due|grand total)[^\d$]*\$?\s*([\d,]+\.\d{2})", re.IGNORECASE
)
INVOICE_NO_RE = re.compile(r"(?:invoice|inv|receipt)\s*(?:no\.?|number|#)?\s*[:\-]?\s*([A-Z0-9\-]{3,20})", re.IGNORECASE)
ABN_RE = re.compile(r"\bABN[:\s]*(\d{2}\s?\d{3}\s?\d{3}\s?\d{3})\b", re.IGNORECASE)
CURRENCY_RE = re.compile(r"\b(AUD|USD|EUR|GBP)\b")


@dataclass
class ParsedInvoice:
    invoice_number: str | None
    invoice_date: str | None  # ISO yyyy-mm-dd
    vendor_abn: str | None
    total_amount: float | None
    currency: str | None

    def to_record(self) -> dict:
        return self.__dict__.copy()


def _parse_date(text: str) -> str | None:
    for pattern, kind in DATE_PATTERNS:
        m = pattern.search(text)
        if not m:
            continue
        if kind == "ymd":
            y, mo, d = m.groups()
        elif kind == "dmy":
            d, mo, y = m.groups()
        else:  # "12 Mar 2026"
            d, mon, y = m.groups()
            mo = MONTHS[mon.lower()[:3]]
        try:
            mo_i, d_i = int(mo), int(d)
            if 1 <= mo_i <= 12 and 1 <= d_i <= 31:
                return f"{int(y):04d}-{mo_i:02d}-{d_i:02d}"
        except ValueError:
            continue
    return None


def parse_invoice_text(text: str) -> ParsedInvoice:
    """Extract structured fields from raw document text."""
    total = None
    if m := TOTAL_RE.search(text):
        total = float(m.group(1).replace(",", ""))

    return ParsedInvoice(
        invoice_number=(m.group(1) if (m := INVOICE_NO_RE.search(text)) else None),
        invoice_date=_parse_date(text),
        vendor_abn=(m.group(1).replace(" ", "") if (m := ABN_RE.search(text)) else None),
        total_amount=total,
        currency=(m.group(1) if (m := CURRENCY_RE.search(text)) else None),
    )
