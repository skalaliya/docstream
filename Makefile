PYTHON ?= python3
VENV = .venv
PIP = $(VENV)/bin/pip
PY = $(VENV)/bin/python

.PHONY: install dev samples pipeline dbt dashboard test lint all

$(VENV):
	$(PYTHON) -m venv $(VENV)

install: $(VENV)  ## create venv + install deps
	$(PIP) install -e ".[dev,serving]"

dev:  ## Dagster UI
	$(VENV)/bin/dagster dev -m pipelines.definitions

samples:  ## generate synthetic invoices into data/landing
	$(PY) scripts/generate_samples.py

dbt:  ## build gold models + run dbt tests
	cd dbt && DBT_PROFILES_DIR=. ../$(VENV)/bin/dbt build

dashboard:
	$(VENV)/bin/streamlit run serving/dashboard.py

test:
	$(PY) -m pytest -q

lint:
	$(VENV)/bin/ruff check .

all: samples test dbt
