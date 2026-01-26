import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from demandcast.config import FORECAST_HORIZON_DAYS, METRIC_NAMES, backtest_config
from demandcast.data.preprocess import load_processed_series
from demandcast.evaluation import RollingBacktestSettings, backtest_model_class
from demandcast.evaluation.reporting import (
    save_json_report,
    save_predictions_csv,
    save_summary_table,
)
from demandcast.logging_utils import get_logger
from demandcast.models import EnsembleConfig, EnsembleForecaster, LGBMForecaster
from demandcast.paths import ensure_directories

logger = get_logger(__name__)


def _configure_root_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _load_existing_metrics(path: Path) -> Dict[str, Any]:
    if not path.exists():
        logger.warning("No existing backtest metrics found at %s", path)
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_ensemble_weights(path: Path) -> Dict[str, float]:
    if not path.exists():
        logger.warning(
            "Ensemble weights file %s not found. Using equal weights for ensemble backtests.",
            path,
        )
        return {}
    with path.open("r", encoding="utf-8") as f:
        weights = json.load(f)
    return {str(k): float(v) for k, v in weights.items()}


def main() -> None:
    _configure_root_logging()
    logger.info("Step 3: Backtesting LightGBM and Ensemble models")

    ensure_directories()

    series_df, series_path = load_processed_series()
    logger.info("Loaded processed series from %s (rows=%d)", series_path, len(series_df))

    settings = RollingBacktestSettings(
        initial_train_days=backtest_config.initial_train_days,
        step_days=backtest_config.step_days,
        horizon_days=FORECAST_HORIZON_DAYS,
        n_folds=backtest_config.n_folds,
    )
    logger.info("Backtest settings: %s", settings.to_dict())

    reports_dir = Path("artifacts") / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = reports_dir / "backtest_metrics.json"
    summary_path = reports_dir / "summary_table.csv"
    model_comparison_path = reports_dir / "model_comparison.csv"
    ensemble_weights_path = reports_dir / "ensemble_weights.json"

    existing_metrics = _load_existing_metrics(metrics_path)
    summary_rows: List[Dict[str, Any]] = []

    if summary_path.exists():
        import pandas as pd

        existing_summary = pd.read_csv(summary_path)
        summary_rows.extend(existing_summary.to_dict(orient="records"))

    models_to_backtest = {
        "lgbm": LGBMForecaster,
    }

    ensemble_weights = _load_ensemble_weights(ensemble_weights_path)
    models_to_backtest["ensemble"] = lambda: EnsembleForecaster(
        config=EnsembleConfig(weights=ensemble_weights)
    )

    combined_metrics = dict(existing_metrics)

    for name, cls in models_to_backtest.items():
        logger.info("Backtesting model '%s'", name)
        preds_df, agg_metrics, fold_results = backtest_model_class(series_df, cls, settings)

        save_predictions_csv(preds_df, name)

        row = {"model": name}
        for metric_name in METRIC_NAMES + ["coverage", "mean_interval_width"]:
            if metric_name in agg_metrics:
                row[metric_name] = agg_metrics[metric_name]
        summary_rows.append(row)

        combined_metrics[name] = {
            "aggregate_metrics": agg_metrics,
            "folds": [fr.metrics for fr in fold_results],
        }

    if summary_rows:
        save_summary_table(summary_rows, "summary_table.csv")
    save_json_report(combined_metrics, "backtest_metrics.json")

    # Build model comparison table including all models
    import pandas as pd

    comparison_rows: List[Dict[str, Any]] = []
    for model_name, content in combined_metrics.items():
        agg = content.get("aggregate_metrics", {})
        row = {"model": model_name}
        for metric_name in METRIC_NAMES + ["coverage", "mean_interval_width"]:
            row[metric_name] = agg.get(metric_name)
        comparison_rows.append(row)

    comparison_df = pd.DataFrame(comparison_rows)
    comparison_df.to_csv(model_comparison_path, index=False)
    logger.info("Saved model comparison table to %s", model_comparison_path)
    logger.info("Step 3 backtests for LGBM and Ensemble completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception(
            "Step 3 backtest script for LGBM and Ensemble failed with unexpected error: %s",
            exc,
        )
        raise