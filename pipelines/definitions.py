"""Dagster definitions — run with: dagster dev -m pipelines.definitions"""

from dagster import Definitions

from pipelines.assets import bronze_documents, extracted_documents, landing_files
from pipelines.silver import silver_invoices

defs = Definitions(
    assets=[landing_files, extracted_documents, bronze_documents, silver_invoices]
)
