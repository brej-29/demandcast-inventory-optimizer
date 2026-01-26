import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pandas as pd

from demandcast.config import FORECAST_HORIZON_DAYS, artifact_config
from demandcast.data.preprocess import load_processed_series
from demandcast.inventory import optimize_inventory
from demandcast.logging_utils import get_logger
from demandcast.models import EnsembleForecaster
from demandcast.paths import ensure_directories

logger = get_logger(__name__)


def _configure_root_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _load_or_fit_ensemble(series_df: pd.DataFrame) -> EnsembleForecaster:
    models_dir = artifact_config.models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    ensemble_path = models_dir / "ensemble.pkl"
    if ensemble_path.exists():
        logger.info("Loading existing ensemble model from %s", ensemble_path)
        return EnsembleForecaster.load(ensemble_path)
    logger.warning(
        "Ensemble model not found at %s; fitting a new ensemble on the fly.", ensemble_path
    )
    ensemble = EnsembleForecaster()
    ensemble.fit(series_df)
    ensemble.save(ensemble_path)
    return ensemble


def main() -> None:
    _configure_root_logging()
    logger.info("Step 4: Inventory planning and scenario analysis")

    ensure_directories()

    series_df, series_path = load_processed_series()
    logger.info("Loaded processed series from %s (rows=%d)", series_path, len(series_df))

    ensemble = _load_or_fit_ensemble(series_df)

    last_ds = pd.to_datetime(series_df["ds"]).max()
    horizon = FORECAST_HORIZON_DAYS
    future_dates = pd.date_range(start=last_ds + pd.Timedelta(days=1), periods=horizon, freq="D")
    future_df = pd.DataFrame({"ds": future_dates})

    forecast_df = ensemble.predict(future_df, horizon=horizon)

    result = optimize_inventory(forecast_df)

    reports_dir = artifact_config.reports_dir
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Save main recommendation
    rec_row = result["optimized_policy"].copy()
    rec_row.update({"scenario": "optimized"})
    rec_df = pd.DataFrame([rec_row])
    rec_path = reports_dir / "inventory_recommendations.csv"
    rec_df.to_csv(rec_path, index=False)

    # Save scenario table
    scenarios = result.get("scenarios", [])
    scen_df = pd.DataFrame(scenarios)
    scen_path = reports_dir / "inventory_scenarios.csv"
    scen_df.to_csv(scen_path, index=False)

    logger.info("Saved inventory recommendations to %s", rec_path)
    logger.info("Saved inventory scenarios to %s", scen_path)
    logger.info("Step 4 inventory planning completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Step 4 inventory planning script failed with unexpected error: %s", exc)
        raise