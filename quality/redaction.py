"""PII redaction applied before any text leaves the governed zone (e.g. embeddings).

Governance principle: embeddings and search indexes are *derived data products* —
PII must be stripped before derivation, not after. Regex-based detectors cover
common identifiers; Microsoft Presidio can be plugged in for NER-based detection
via the same ``redact`` interface.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PATTERNS: dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    "PHONE_AU": re.compile(r"(?<!\d)(?:\+?61|0)[ -]?[2-478](?:[ -]?\d){8}(?!\d)"),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "TFN": re.compile(r"\bTFN[:\s]*\d{3}\s?\d{3}\s?\d{3}\b", re.IGNORECASE),
    "MEDICARE": re.compile(r"\bMedicare[:\s]*\d{4}\s?\d{5}\s?\d\b", re.IGNORECASE),
}


@dataclass
class RedactionReport:
    text: str
    counts: dict[str, int]

    @property
    def total_redactions(self) -> int:
        return sum(self.counts.values())


def redact(text: str) -> RedactionReport:
    """Replace detected PII with typed placeholders, e.g. ``[REDACTED:EMAIL]``."""
    counts: dict[str, int] = {}
    for label, pattern in PATTERNS.items():
        text, n = pattern.subn(f"[REDACTED:{label}]", text)
        if n:
            counts[label] = n
    return RedactionReport(text=text, counts=counts)
