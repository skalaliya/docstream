"""Tests for the extraction layer."""

from pathlib import Path

from pypdf import PdfWriter

from pipelines.extraction import NativeExtractor, get_extractor


def _make_pdf(path: Path, pages: int = 2) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with path.open("wb") as f:
        writer.write(f)
    return path


def test_native_extractor_pdf(tmp_path: Path):
    pdf = _make_pdf(tmp_path / "sample.pdf", pages=3)
    result = NativeExtractor().extract(pdf)
    assert result.page_count == 3
    assert result.extractor == "native"
    assert len(result.source_sha256) == 64


def test_extraction_result_record(tmp_path: Path):
    pdf = _make_pdf(tmp_path / "sample.pdf")
    record = NativeExtractor().extract(pdf).to_record()
    assert record["char_count"] == len(record["text"])
    assert "source_sha256" in record


def test_get_extractor_returns_extractor():
    ex = get_extractor()
    assert hasattr(ex, "extract")
    assert ex.name in {"native", "docling"}


def test_dedupe_hash_stable(tmp_path: Path):
    pdf = _make_pdf(tmp_path / "sample.pdf")
    r1 = NativeExtractor().extract(pdf)
    r2 = NativeExtractor().extract(pdf)
    assert r1.source_sha256 == r2.source_sha256
