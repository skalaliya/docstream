"""Dagster definitions — run with: dagster dev -m pipelines.definitions"""

from dagster import Definitions

from pipelines.assets import bronze_documents, extracted_documents, landing_files
from pipelines.sensors import ingest_job, landing_zone_sensor
from pipelines.serving_assets import vector_index
from pipelines.silver import silver_invoices

defs = Definitions(
    assets=[landing_files, extracted_documents, bronze_documents, silver_invoices, vector_index],
    jobs=[ingest_job],
    sensors=[landing_zone_sensor],
)
