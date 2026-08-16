"""Central configuration for DocStream."""

import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("DOCSTREAM_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
LANDING_DIR = DATA_DIR / "landing"
BRONZE_DIR = DATA_DIR / "bronze" / "documents"

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}
