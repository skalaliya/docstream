"""Operational monitoring: landing-zone sensor triggers the pipeline on new files."""

from __future__ import annotations

from dagster import (
    AssetSelection,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    define_asset_job,
    sensor,
)

from pipelines.config import LANDING_DIR, SUPPORTED_EXTENSIONS

ingest_job = define_asset_job("ingest_job", selection=AssetSelection.all())


@sensor(job=ingest_job, minimum_interval_seconds=60)
def landing_zone_sensor(context: SensorEvaluationContext):
    """Fire a run when unseen files appear in the landing zone (cursor = seen paths)."""
    seen = set((context.cursor or "").split("\n")) if context.cursor else set()
    current = {
        str(p)
        for p in LANDING_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    }
    new = current - seen
    if not new:
        return SkipReason("No new files in landing zone.")
    context.update_cursor("\n".join(sorted(current)))
    return RunRequest(run_key=f"landing-{len(current)}-{hash(frozenset(new)) & 0xFFFF}")
