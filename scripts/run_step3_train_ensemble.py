import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from demandcast.config import METRIC_NAMES, artifact_config
from demandcast.data.preprocess import load_processed_series
from demandcast.logging_utils import get_logger
from demandcast.models import EnsembleForecaster, EnsembleConfig
from demandcast.paths import DEMO_ARTIFACTS_DIR, ensure_directories

logger = get_logger(__name__)


def _configure_root_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _load_backtest_metrics(path: Path) -> Dict[str, Any]:
    if not path.exists():
        logger.warning(
            "Backtest metrics file %s not found. Ensemble will use equal weights.",
            path,
        )
        return {}
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload


def _compute_weights_from_metrics(metrics_payload: Dict[str, Any]) -> Dict[str, float]:
    if not metrics_payload:
        return {}

    weights: Dict[str, float] = {}
    for model_name, content in metrics_payload.items():
        agg = content.get("aggregate_metrics", {})
        wape = agg.get("wape")
        if wape is None:
            logger.warning("No WAPE metric for model '%s'; assigning zero weight.", model_name)
            weights[model_name] = 0.0
            continue
        try:
            wape_val = float(wape)
        except (TypeError, ValueError):
            logger.warning(
                "Non-numeric WAPE metric for model '%s' (%r); assigning zero weight.",
                model_name,
                wape,
            )
            weights[model_name] = 0.0
            continue

        if wape_val <= 0.0:
            score = 1.0
        else:
            score = 1.0 / wape_val
        weights[model_name] = score

    logger.info("Raw ensemble weights from metrics: %s", weights)
    return weights


def main() -> None:
    _configure_root_logging()
    logger.info("Step 3: Training ensemble forecaster")

    ensure_directories()

    series_df, series_path = load_processed_series()
    logger.info("Loaded processed series from %s (rows=%d)", series_path, len(series_df))

    reports_dir = artifact_config.reports_dir
    reports_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = reports_dir / "backtest_metrics.json"

    metrics_payload = _load_backtest_metrics(metrics_path)
    raw_weights = _compute_weights_from_metrics(metrics_payload)

    config = EnsembleConfig(weights=raw_weights)
    ensemble = EnsembleForecaster(config=config)
    ensemble.fit(series_df)

    models_dir = artifact_config.models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    ensemble_path = models_dir / "ensemble.pkl"
    ensemble.save(ensemble_path)

    weights_path = reports_dir / "ensemble_weights.json"
    ensemble.save_weights(weights_path)

    logger.info("Saved ensemble model to %s", ensemble_path)
    logger.info("Saved ensemble weights to %s", weights_path)
    logger.info("Step 3 ensemble training completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Step 3 ensemble training script failed with unexpected error: %s", exc)
        raise