# DocStream

[![CI](https://github.com/skalaliya/docstream/actions/workflows/ci.yml/badge.svg)](https://github.com/skalaliya/docstream/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**AI-ready document data pipeline** — ingests messy real-world documents (invoices, receipts, reports), extracts structured data with layout-aware OCR, and lands it in a governed medallion lakehouse serving both analytics and RAG.

> Built by [Sam Kalaliya](https://github.com/skalaliya) · Sydney, Australia

## Why

Most AI projects fail on data, not models. DocStream demonstrates the unglamorous work that makes AI work: turning raw documents into **AI-ready datasets** with quality gates, quarantine, lineage, deduplication, and PII governance built in from day one.

## Architecture

```
PDFs / images
   │  landing zone (data/landing) ── Dagster sensor auto-triggers on new files
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
Serving ───── PII-redacted embeddings → Qdrant (RAG-ready) · Streamlit dashboard
```

Orchestrated with **Dagster** (asset lineage, sensors, observability), all services in **docker-compose** (Dagster UI, Qdrant, MinIO).

## Quickstart

```bash
make install                       # pip install -e ".[dev,serving]"
make samples                       # generate synthetic invoices (no real PII)
make dev                           # Dagster UI at http://localhost:3000 — materialize all
make dbt                           # build gold marts + run dbt tests
make dashboard                     # Streamlit spend analytics
make test                          # 15 unit tests
```

Or everything containerized: `docker compose up`.

## Governance & data quality

- **Quality gates, not silent drops** — records failing Pandera validation are quarantined with an explicit reason, preserving auditability.
- **PII redaction before derivation** — emails, phone numbers, cards, TFN/Medicare identifiers are stripped *before* text is embedded; vector indexes are treated as derived data products.
- **Idempotency everywhere** — sha256 content hashing (bronze dedupe) and UUIDv5 point ids (Qdrant upserts) make every stage safely re-runnable.
- **Lineage** — Dagster asset graph plus dbt docs give end-to-end column-level visibility.

## Security testing

Every pull request and a weekly schedule run [Strix](https://github.com/usestrix/strix) — autonomous AI pentest agents that exercise the code dynamically and validate findings with real proofs-of-concept, rather than static-analysis guesses. On PRs the scan is diff-scoped to changed files. In a governed clinical-data pipeline, security is part of the quality contract, not an afterthought. See `.github/workflows/security-scan.yml`.

## Design decisions

- **Strategy-pattern extractors & embedders** — swap OCR engines (docling → HF VLM → cloud OCR) or embedding models without touching pipeline code; CI runs on zero-model fallbacks, so tests never download weights.
- **Medallion layers** — quality is enforced progressively; each layer has a contract.
- **Local & reproducible** — no cloud account needed; synthetic sample data generator included.

## Repo map

```
pipelines/    Dagster assets, sensor, config (ingestion → bronze → silver → serving)
quality/      Pandera schemas, quarantine logic, PII redaction
dbt/          staging + marts models, tests, DuckDB profile
serving/      embedders, Qdrant loader, semantic search, Streamlit dashboard
scripts/      synthetic sample-invoice generator
tests/        15 unit tests (extraction, parsing, validation, redaction, embeddings)
```

## Roadmap

- [x] Week 1 — ingestion, extraction, bronze Delta layer, CI
- [x] Week 2 — Pandera silver gates + quarantine, dbt gold models (DuckDB) with tests
- [x] Week 3 — PII redaction, embeddings → Qdrant, Streamlit dashboard
- [x] Week 4 — landing-zone sensor, sample generator, Makefile, docs

## License

MIT © 2026 Sam Kalaliya
