from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = REPO_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

ARTIFACTS_DIR = REPO_ROOT / "artifacts"
MODELS_DIR = ARTIFACTS_DIR / "models"
REPORTS_DIR = ARTIFACTS_DIR / "reports"

ASSETS_DIR = REPO_ROOT / "assets"
DEMO_DATA_DIR = ASSETS_DIR / "demo"
DEMO_ARTIFACTS_DIR = ASSETS_DIR / "demo_artifacts"


def ensure_directories() -> None:
    for path in (
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        ARTIFACTS_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        ASSETS_DIR,
        DEMO_DATA_DIR,
        DEMO_ARTIFACTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


__all__ = [
    "REPO_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "ARTIFACTS_DIR",
    "MODELS_DIR",
    "REPORTS_DIR",
    "ASSETS_DIR",
    "DEMO_DATA_DIR",
    "DEMO_ARTIFACTS_DIR",
    "ensure_directories",
]