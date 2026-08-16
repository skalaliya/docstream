"""Document extraction layer.

Strategy pattern with two extractors:

- ``DoclingExtractor`` — uses IBM's docling (layout-aware parsing) when installed.
- ``NativeExtractor``  — dependency-light fallback: pypdf text extraction for PDFs,
  basic image metadata for images. Keeps the pipeline runnable anywhere (CI, laptops)
  without GPU/large model downloads.

A vision-language OCR model (e.g. an HF image-text-to-text model) can be plugged in
by implementing :class:`Extractor`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol


@dataclass
class ExtractionResult:
    """Normalized output of any extractor — the bronze-layer record."""

    source_path: str
    source_sha256: str
    extractor: str
    extracted_at: str
    page_count: int
    text: str
    metadata: dict = field(default_factory=dict)

    def to_record(self) -> dict:
        return {
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "extractor": self.extractor,
            "extracted_at": self.extracted_at,
            "page_count": self.page_count,
            "text": self.text,
            "char_count": len(self.text),
            **{f"meta_{k}": str(v) for k, v in self.metadata.items()},
        }


class Extractor(Protocol):
    name: str

    def extract(self, path: Path) -> ExtractionResult: ...


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class NativeExtractor:
    """Fallback extractor: pypdf for PDFs, Pillow metadata for images."""

    name = "native"

    def extract(self, path: Path) -> ExtractionResult:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(path)
            text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
            return ExtractionResult(
                source_path=str(path),
                source_sha256=_sha256(path),
                extractor=self.name,
                extracted_at=_now(),
                page_count=len(reader.pages),
                text=text,
                metadata={"producer": reader.metadata.producer if reader.metadata else ""},
            )
        # Image: no OCR in fallback — record metadata, flag for OCR-capable extractor.
        from PIL import Image

        with Image.open(path) as img:
            width, height = img.size
        return ExtractionResult(
            source_path=str(path),
            source_sha256=_sha256(path),
            extractor=self.name,
            extracted_at=_now(),
            page_count=1,
            text="",
            metadata={"width": width, "height": height, "needs_ocr": True},
        )


class DoclingExtractor:
    """Layout-aware extraction via docling (optional dependency)."""

    name = "docling"

    def extract(self, path: Path) -> ExtractionResult:
        from docling.document_converter import DocumentConverter

        result = DocumentConverter().convert(str(path))
        doc = result.document
        return ExtractionResult(
            source_path=str(path),
            source_sha256=_sha256(path),
            extractor=self.name,
            extracted_at=_now(),
            page_count=len(doc.pages) if getattr(doc, "pages", None) else 1,
            text=doc.export_to_markdown(),
        )


def get_extractor() -> Extractor:
    """Prefer docling if installed; otherwise use the native fallback."""
    try:
        import docling  # noqa: F401

        return DoclingExtractor()
    except ImportError:
        return NativeExtractor()
