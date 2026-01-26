import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pandas as pd

from demandcast.data.synthetic import generate_demo_series
from demandcast.evaluation import RollingBacktestSettings, backtest_model_class
from demandcast.logging_utils import get_logger
from demandcast.models import (
    ARIMASARIMAXModel,
    ETSModel,
    LGBMForecaster,
    ProphetFallbackModel,
    EnsembleConfig,
    EnsembleForecaster,
)
from demandcast.paths import DEMO_ARTIFACTS_DIR, DEMO_DATA_DIR, ensure_directories

logger = get_logger(__name__)


def _configure_root_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    _configure_root_logging()
    logger.info("Building demo assets (synthetic series, models, and reports)")

    ensure_directories()
    DEMO_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DEMO_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    series_df = generate_demo_series()
    series_df.to_csv(DEMO_DATA_DIR / "demo_series.csv", index=False)

    settings = RollingBacktestSettings(
        initial_train_days=60,
        step_days=14,
        horizon_days=14,
        n_folds=3,
    )

    model_classes = {
        "sarimax": ARIMASARIMAXModel,
        "ets": ETSModel,
        "prophet_or_fallback": ProphetFallbackModel,
        "lgbm": LGBMForecaster,
    }

    combined_metrics: Dict[str, Any] = {}
    for name, cls in model_classes.items():
        logger.info("Backtesting demo model '%s'", name)
        preds_df, agg_metrics, fold_results = backtest_model_class(series_df, cls, settings)
        preds_df.to_csv(DEMO_ARTIFACTS_DIR / f"predictions_{name}.csv", index=False)
        combined_metrics[name] = {
            "aggregate_metrics": agg_metrics,
            "folds": [fr.metrics for fr in fold_results],
        }

    # Simple inverse-WAPE weights for ensemble.
    weights: Dict[str, float] = {}
    for name, content in combined_metrics.items():
        wape = content["aggregate_metrics"].get("wape", 0.0)
        if wape and wape > 0:
            weights[name] = 1.0 / float(wape)
    cfg = EnsembleConfig(weights=weights)
    ensemble = EnsembleForecaster(config=cfg)
    ensemble.fit(series_df)

    from demandcast.config import FORECAST_HORIZON_DAYS

    last_ds = series_df["ds"].max()
    future_ds = pd.date_range(
        start=last_ds + pd.Timedelta(days=1), periods=FORECAST_HORIZON_DAYS, freq="D"
    )
    future_df = pd.DataFrame({"ds": future_ds})
    ens_preds = ensemble.predict(future_df, horizon=FORECAST_HORIZON_DAYS)
    ens_preds.to_csv(DEMO_ARTIFACTS_DIR / "predictions_ensemble.csv", index=False)

    # Persist model-comparison-style table.
    rows: List[Dict[str, Any]] = []
    for name, content in combined_metrics.items():
        row = {"model": name}
        row.update(content["aggregate_metrics"])
        rows.append(row)
    pd.DataFrame(rows).to_csv(DEMO_ARTIFACTS_DIR / "model_comparison.csv", index=False)

    # Save ensemble weights JSON
    import json

    weights_path = DEMO_ARTIFACTS_DIR / "ensemble_weights.json"
    with weights_path.open("w", encoding="utf-8") as f:
        json.dump(ensemble.config.weights, f, indent=2)

    logger.info("Demo assets created under %s and %s", DEMO_DATA_DIR, DEMO_ARTIFACTS_DIR)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error while building demo assets: %s", exc)
        raise