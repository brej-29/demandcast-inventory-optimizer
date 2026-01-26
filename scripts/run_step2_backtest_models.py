import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from demandcast.config import FORECAST_HORIZON_DAYS, backtest_config
from demandcast.data.preprocess import load_processed_series
from demandcast.evaluation import RollingBacktestSettings, backtest_model_class
from demandcast.evaluation.reporting import (
    save_json_report,
    save_predictions_csv,
    save_summary_table,
)
from demandcast.logging_utils import get_logger
from demandcast.models import ARIMASARIMAXModel, ETSModel, ProphetFallbackModel
from demandcast.paths import ensure_directories

logger = get_logger(__name__)


def _configure_root_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    _configure_root_logging()
    logger.info("Step 2: Running rolling-origin backtests for baseline models")

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

    model_classes = {
        "sarimax": ARIMASARIMAXModel,
        "ets": ETSModel,
        "prophet_or_fallback": ProphetFallbackModel,
    }

    summary_rows: List[Dict[str, Any]] = []
    metrics_payload: Dict[str, Any] = {}

    for name, cls in model_classes.items():
        logger.info("Backtesting model '%s'", name)
        preds_df, agg_metrics, fold_results = backtest_model_class(
            series_df, cls, settings
        )

        save_predictions_csv(preds_df, name)

        row = {"model": name}
        row.update(agg_metrics)
        metrics_payload[name] = {
            "aggregate_metrics": agg_metrics,
            "folds": [fr.metrics for fr in fold_results],
        }
        summary_rows.append(row)

    if summary_rows:
        save_summary_table(summary_rows, "summary_table.csv")
        save_json_report(metrics_payload, "backtest_metrics.json")

    logger.info("Step 2 backtests completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Step 2 backtest script failed with unexpected error: %s", exc)
        raise