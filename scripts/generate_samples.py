"""Generate synthetic sample invoices (PDF) into data/landing for demos.

Synthetic data only — no real PII. Usage: python scripts/generate_samples.py [n]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

LANDING = Path(__file__).resolve().parents[1] / "data" / "landing"

VENDORS = [
    ("ACME Supplies Pty Ltd", "51 824 753 556"),
    ("Harbour Office Co", "12 345 678 901"),
    ("Southern Cross IT", "98 765 432 109"),
]


def make_invoice_pdf(path: Path, vendor: str, abn: str, number: str, date: str, total: float):
    text = (
        f"{vendor}\nABN: {abn}\nInvoice No: {number}\nDate: {date}\n"
        f"Total Amount Due: ${total:,.2f} AUD\nThank you for your business."
    )
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    # Minimal text content stream
    stream = DecodedStreamObject()
    lines = "".join(
        f"BT /F1 12 Tf 72 {720 - i * 20} Td ({line}) Tj ET\n" for i, line in enumerate(text.split("\n"))
    )
    stream.set_data(lines.encode())
    page[NameObject("/Contents")] = writer._add_object(stream)
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {
                    NameObject("/F1"): DictionaryObject(
                        {
                            NameObject("/Type"): NameObject("/Font"),
                            NameObject("/Subtype"): NameObject("/Type1"),
                            NameObject("/BaseFont"): NameObject("/Helvetica"),
                        }
                    )
                }
            )
        }
    )
    with path.open("wb") as f:
        writer.write(f)


def main(n: int = 6):
    LANDING.mkdir(parents=True, exist_ok=True)
    random.seed(42)
    for i in range(n):
        vendor, abn = random.choice(VENDORS)
        month = random.randint(1, 6)
        make_invoice_pdf(
            LANDING / f"invoice_{i:03d}.pdf",
            vendor,
            abn,
            f"INV-2026-{i:04d}",
            f"2026-{month:02d}-{random.randint(1, 28):02d}",
            round(random.uniform(50, 5000), 2),
        )
    print(f"Wrote {n} sample invoices to {LANDING}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6)
