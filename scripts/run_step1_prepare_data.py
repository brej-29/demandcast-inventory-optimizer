import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from demandcast.config import (
    DATA_RAW_DIR,
    DEFAULT_ITEM_ID,
    DEFAULT_SERIES_MODE,
    DEFAULT_STORE_ID,
    KAGGLE_COMPETITION,
    RAW_TRAIN_FILENAME,
    load_settings_from_env_or_defaults,
)
from demandcast.data import (
    build_target_series,
    load_kaggle_train_df,
    locate_kaggle_train_csv,
)
from demandcast.data.preprocess import save_processed_series
from demandcast.data.validate import compute_basic_series_diagnostics
from demandcast.evaluation.reporting import save_json_report
from demandcast.logging_utils import get_logger
from demandcast.paths import REPO_ROOT, ensure_directories

logger = get_logger(__name__)


def _configure_root_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _summarize_settings(settings: Dict[str, Any]) -> None:
    logger.info("Using settings:")
    for k, v in settings.items():
        logger.info("  %s = %s", k, v)


def main() -> None:
    _configure_root_logging()
    logger.info("Step 1: Preparing data")

    ensure_directories()

    settings = load_settings_from_env_or_defaults()
    _summarize_settings(settings)

    try:
        csv_path = locate_kaggle_train_csv()
    except FileNotFoundError:
        logger.error(
            "Kaggle training data not found under %s (expected %s).",
            DATA_RAW_DIR,
            RAW_TRAIN_FILENAME,
        )
        logger.error(
            "Download it using the Kaggle CLI, for example:\n"
            "  kaggle competitions download -c %s -p data/raw\n"
            "or run one of the helper scripts:\n"
            "  bash scripts/download_kaggle_competition.sh\n"
            "  pwsh scripts/download_kaggle_competition.ps1",
            KAGGLE_COMPETITION,
        )
        raise

    train_df = load_kaggle_train_df(csv_path)

    series_mode = settings.get("series_mode", DEFAULT_SERIES_MODE)
    store_id = settings.get("store_id", DEFAULT_STORE_ID)
    item_id = settings.get("item_id", DEFAULT_ITEM_ID)

    series_df = build_target_series(
        train_df,
        mode=series_mode,
        store_id=store_id,
        item_id=item_id,
    )

    output_path = save_processed_series(series_df)

    diagnostics = compute_basic_series_diagnostics(series_df)
    summary_payload: Dict[str, Any] = {
        "repo_root": str(REPO_ROOT),
        "raw_data_dir": str(DATA_RAW_DIR),
        "train_csv": str(csv_path),
        "processed_series_path": str(output_path),
        "series_mode": series_mode,
        "store_id": store_id,
        "item_id": item_id,
        "diagnostics": diagnostics.to_dict(),
    }

    save_json_report(summary_payload, "data_summary.json")

    logger.info("Step 1 completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Step 1 failed with an unexpected error: %s", exc)
        raise