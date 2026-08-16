"""Tests for redaction and embedding layers."""

from quality.redaction import redact
from serving.embeddings import HashingEmbedder, get_embedder


def test_redact_email_and_phone():
    text = "Contact john.smith@example.com or 0412 345 678 for details."
    report = redact(text)
    assert "[REDACTED:EMAIL]" in report.text
    assert "[REDACTED:PHONE_AU]" in report.text
    assert "john.smith" not in report.text
    assert report.total_redactions == 2


def test_redact_clean_text_untouched():
    text = "Invoice INV-2026-0042 total $1,234.56 AUD"
    report = redact(text)
    assert report.text == text
    assert report.total_redactions == 0


def test_redact_credit_card():
    report = redact("Card: 4111 1111 1111 1111")
    assert "[REDACTED:CREDIT_CARD]" in report.text


def test_hashing_embedder_deterministic_and_normalized():
    e = HashingEmbedder()
    v1, v2 = e.embed(["hello world"]), e.embed(["hello world"])
    assert v1 == v2
    assert len(v1[0]) == e.dim
    norm = sum(x * x for x in v1[0]) ** 0.5
    assert abs(norm - 1.0) < 1e-9


def test_hashing_embedder_distinguishes_texts():
    e = HashingEmbedder()
    a, b = e.embed(["invoice from acme", "completely different words here"])
    assert a != b


def test_get_embedder_interface():
    e = get_embedder()
    assert hasattr(e, "embed") and e.dim > 0
