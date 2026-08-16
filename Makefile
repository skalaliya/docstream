.PHONY: install dev samples pipeline dbt dashboard test lint all

install:
	pip install -e ".[dev,serving]"

dev:  ## Dagster UI
	dagster dev -m pipelines.definitions

samples:  ## generate synthetic invoices into data/landing
	python scripts/generate_samples.py

dbt:  ## build gold models + run dbt tests
	cd dbt && DBT_PROFILES_DIR=. dbt build

dashboard:
	streamlit run serving/dashboard.py

test:
	pytest -q

lint:
	ruff check .

all: samples test dbt
