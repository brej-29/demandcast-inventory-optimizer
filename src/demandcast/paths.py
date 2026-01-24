from pathlib import Path

# Resolve repository root assuming a src/ layout:
# repo_root/
#   src/demandcast/paths.py
REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = REPO_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

ARTIFACTS_DIR = REPO_ROOT / "artifacts"
MODELS_DIR = ARTIFACTS_DIR / "models"
REPORTS_DIR = ARTIFACTS_DIR / "reports"


__all__ = [
    "REPO_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "ARTIFACTS_DIR",
    "MODELS_DIR",
    "REPORTS_DIR",
]