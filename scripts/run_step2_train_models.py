import json
import logging
import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from demandcast.config import artifact_config
from demandcast.data.preprocess import load_processed_series
from demandcast.logging_utils import get_logger
from demandcast.models import ARIMASARIMAXModel, ETSModel, ProphetFallbackModel
from demandcast.paths import ensure_directories
from demandcast.evaluation.reporting import save_json_report

logger = get_logger(__name__)


def _configure_root_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _save_model(model: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(model, f)
    logger.info("Saved model to %s", path)


def main() -> None:
    _configure_root_logging()
    logger.info("Step 2: Training baseline models (SARIMAX, ETS, Prophet-or-fallback)")

    ensure_directories()

    series_df, series_path = load_processed_series()
    logger.info("Loaded processed series from %s (rows=%d)", series_path, len(series_df))

    models_to_train: Dict[str, Any] = {
        "sarimax": ARIMASARIMAXModel,
        "ets": ETSModel,
        "prophet_or_fallback": ProphetFallbackModel,
    }

    model_paths: Dict[str, str] = {}
    failures: Dict[str, str] = {}

    for name, cls in models_to_train.items():
        logger.info("Training model '%s'", name)
        try:
            model = cls()
            model.fit(series_df)
            out_path = artifact_config.models_dir / f"{name}.pkl"
            _save_model(model, out_path)
            model_paths[name] = str(out_path)
        except Exception as exc:
            logger.exception("Training of model '%s' failed: %s", name, exc)
            failures[name] = str(exc)

    payload: Dict[str, Any] = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "models": model_paths,
        "failures": failures,
    }
    save_json_report(payload, "train_step2_models.json")

    if failures:
        logger.warning("Some models failed during training: %s", failures)
    else:
        logger.info("All baseline models trained successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Step 2 training script failed with unexpected error: %s", exc)
        raise