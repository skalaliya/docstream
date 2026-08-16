# DocStream

**AI-ready document data pipeline** — ingests messy real-world documents (invoices, receipts, reports), extracts structured data with layout-aware OCR, and lands it in a governed medallion lakehouse ready for both analytics and RAG.

> Built by [Sam Kalaliya](https://github.com/skalaliya) · Sydney, Australia

## Why

Most AI projects fail on data, not models. DocStream demonstrates the unglamorous work that makes AI work: turning raw documents into **AI-ready datasets** with quality gates, lineage, deduplication, and governance built in from day one.

## Architecture

```
PDFs / images
   │  landing zone (data/landing)
   ▼
Extraction ── docling (layout-aware) with dependency-light native fallback
   │           pluggable: any HF vision-language OCR model via the Extractor protocol
   ▼
Bronze ────── raw extraction records, Delta Lake, sha256-deduped, idempotent
   ▼
Silver ────── parsed invoice fields, Pandera gates, quarantine for failures
   ▼
Gold ──────── dbt + DuckDB marts (dim_vendors, fct_monthly_spend) with dbt tests
   ▼
Serving ───── embeddings → Qdrant (RAG-ready) · Streamlit dashboard  [week 3]
```

Orchestrated with **Dagster** (asset lineage + observability), all services in **docker-compose** (Dagster UI, Qdrant, MinIO).

## Quickstart

```bash
pip install -e ".[dev]"          # add ".[ocr]" for docling
# drop PDFs/images into data/landing/
dagster dev -m pipelines.definitions          # open http://localhost:3000, materialize assets
pytest                            # run tests
```

Or everything at once: `docker compose up`.

## Design decisions

- **Strategy-pattern extractors** — swap OCR engines (docling, HF VLM, cloud OCR) without touching pipeline code; CI runs on the zero-model fallback.
- **Idempotent bronze writes** — sha256 content hashing means re-runs never duplicate data.
- **Medallion layers** — quality is enforced progressively; bad data is quarantined, not silently dropped.
- **Everything local & reproducible** — no cloud account needed to run the full stack.

## Roadmap

- [x] Week 1 — ingestion, extraction, bronze Delta layer, CI
- [x] Week 2 — Pandera silver gates + quarantine, dbt gold models (DuckDB) with tests
- [ ] Week 3 — embeddings → Qdrant, PII redaction (presidio), Streamlit dashboard
- [ ] Week 4 — monitoring/sensors, demo GIF, v1.0 release

## License

MIT © 2026 Sam Kalaliya
