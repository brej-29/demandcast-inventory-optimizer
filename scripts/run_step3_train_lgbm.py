import logging
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

from demandcast.config import artifact_config
from demandcast.data.preprocess import load_processed_series
from demandcast.features import (
    FeatureConfig,
    build_time_series_features,
    get_default_feature_columns,
    make_supervised_dataset,
)
from demandcast.logging_utils import get_logger
from demandcast.models import LGBMForecaster
from demandcast.paths import ensure_directories

logger = get_logger(__name__)


def _configure_root_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _compute_gain_importance(
    regressor,
    feature_names,
) -> pd.DataFrame:
    importances = getattr(regressor, "feature_importances_", None)
    if importances is None:
        raise RuntimeError("Regressor does not expose feature_importances_ attribute.")
    df = pd.DataFrame({"feature": feature_names, "importance": importances})
    df = df.sort_values("importance", ascending=False).reset_index(drop=True)
    return df


def _compute_permutation_importance(
    regressor,
    X_val: pd.DataFrame,
    y_val: pd.Series,
) -> pd.DataFrame:
    result = permutation_importance(
        regressor,
        X_val,
        y_val,
        n_repeats=5,
        random_state=42,
        n_jobs=-1,
    )
    importances_mean = result.importances_mean
    importances_std = result.importances_std
    df = pd.DataFrame(
        {
            "feature": X_val.columns,
            "importance_mean": importances_mean,
            "importance_std": importances_std,
        }
    )
    df = df.sort_values("importance_mean", ascending=False).reset_index(drop=True)
    return df


def main() -> None:
    _configure_root_logging()
    logger.info("Step 3: Training LightGBM forecaster and computing feature importances")

    ensure_directories()

    series_df, series_path = load_processed_series()
    logger.info("Loaded processed series from %s (rows=%d)", series_path, len(series_df))

    forecaster = LGBMForecaster()
    forecaster.fit(series_df)

    models_dir = artifact_config.models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    lgbm_path = models_dir / "lgbm.pkl"
    forecaster.save(lgbm_path)
    logger.info("Saved trained LGBMForecaster to %s", lgbm_path)

    features_df = build_time_series_features(series_df, config=FeatureConfig())
    feature_cols = get_default_feature_columns(features_df)
    X, y = make_supervised_dataset(features_df, feature_cols=feature_cols, target_col="y")

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        shuffle=False,
    )

    reg = forecaster._regressor
    if reg is None:
        raise RuntimeError("LGBMForecaster._regressor is not fitted.")

    gain_df = _compute_gain_importance(reg, feature_cols)
    perm_df = _compute_permutation_importance(reg, X_val, y_val)

    reports_dir = artifact_config.reports_dir
    reports_dir.mkdir(parents=True, exist_ok=True)

    gain_path = reports_dir / "lgbm_feature_importance_gain.csv"
    perm_path = reports_dir / "lgbm_permutation_importance.csv"

    gain_df.to_csv(gain_path, index=False)
    perm_df.to_csv(perm_path, index=False)

    logger.info("Saved LightGBM gain feature importance to %s", gain_path)
    logger.info("Saved LightGBM permutation importance to %s", perm_path)
    logger.info("Step 3 LGBM training completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Step 3 LGBM training script failed with unexpected error: %s", exc)
        raise