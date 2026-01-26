from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor

from ..config import FORECAST_HORIZON_DAYS
from ..features import (
    FeatureConfig,
    build_time_series_features,
    get_default_feature_columns,
    make_supervised_dataset,
)
from ..logging_utils import get_logger
from .intervals import build_mapie_timeseries_regressor

logger = get_logger(__name__)


@dataclass
class LGBMConfig:
    n_estimators: int = 200
    learning_rate: float = 0.05
    max_depth: int = -1
    subsample: float = 0.9
    colsample_bytree: float = 0.9
    random_state: int = 42
    alpha: float = 0.1  # miscoverage (0.1 -> 90% intervals)


class LGBMForecaster:
    """
    Gradient boosting forecaster built on top of LightGBM.

    Uses lag / rolling / calendar features and a recursive multi-step strategy.
    Prediction intervals use MAPIE EnbPI when available, otherwise a simple
    empirical residual-based approach.
    """

    def __init__(self, config: Optional[LGBMConfig] = None) -> None:
        self.config = config or LGBMConfig()
        self._regressor: Optional[LGBMRegressor] = None
        self._mapie = None
        self._feature_cols: List[str] = []
        self._feature_config = FeatureConfig()
        self._history_df: Optional[pd.DataFrame] = None

    def _build_features(self, series_df: pd.DataFrame) -> pd.DataFrame:
        features_df = build_time_series_features(series_df, config=self._feature_config)
        return features_df

    def fit(self, series_df: pd.DataFrame) -> "LGBMForecaster":
        df = series_df.copy()
        if "ds" not in df.columns or "y" not in df.columns:
            raise ValueError("Series DataFrame must contain 'ds' and 'y' columns.")

        df = df.sort_values("ds").reset_index(drop=True)
        self._history_df = df[["ds", "y"]].copy()
        features_df = self._build_features(df)
        self._feature_cols = get_default_feature_columns(features_df)

        X, y = make_supervised_dataset(features_df, feature_cols=self._feature_cols, target_col="y")

        logger.info(
            "Training LGBMForecaster on supervised dataset X=%s, y_len=%d",
            X.shape,
            len(y),
        )

        self._regressor = LGBMRegressor(
            n_estimators=self.config.n_estimators,
            learning_rate=self.config.learning_rate,
            max_depth=self.config.max_depth,
            subsample=self.config.subsample,
            colsample_bytree=self.config.colsample_bytree,
            random_state=self.config.random_state,
            n_jobs=-1,
        )
        self._regressor.fit(X, y)

        self._mapie = build_mapie_timeseries_regressor(
            base_estimator=self._regressor,
            alpha=self.config.alpha,
            random_state=self.config.random_state,
        )
        if self._mapie is not None:
            logger.info("Fitting MAPIE time-series regressor for conformal intervals.")
            self._mapie.fit(X, y)

        return self

    def _predict_stepwise(
        self,
        history_df: pd.DataFrame,
        horizon: int,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[pd.Timestamp]]:
        if self._regressor is None:
            raise RuntimeError("LGBMForecaster has not been fitted yet.")

        df_all = history_df.copy().sort_values("ds").reset_index(drop=True)
        last_date = df_all["ds"].max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

        yhat_list: List[float] = []
        lower_list: List[float] = []
        upper_list: List[float] = []
        ds_list: List[pd.Timestamp] = []

        residuals: Optional[np.ndarray] = None
        if self._mapie is None:
            features_df = self._build_features(df_all)
            X_train, y_train = make_supervised_dataset(
                features_df,
                feature_cols=self._feature_cols,
                target_col="y",
            )
            y_pred_train = self._regressor.predict(X_train)
            residuals = (y_train.to_numpy() - y_pred_train).astype(float)
            if residuals.size == 0:
                residuals = np.array([0.0])
            logger.info(
                "Using empirical residual quantiles for intervals (MAPIE not available). "
                "Residual count=%d",
                residuals.size,
            )

        for offset, current_date in enumerate(future_dates, start=1):
            tmp = df_all.copy()
            features_df = self._build_features(tmp)
            row = features_df[features_df["ds"] == tmp["ds"].max()]
            if row.empty:
                logger.warning(
                    "No feature row found for date %s; stopping recursive forecast at step %d.",
                    current_date,
                    offset,
                )
                break

            X_current = row[self._feature_cols]

            if self._mapie is not None:
                preds, intervals = self._mapie.predict(X_current, alpha=self.config.alpha)
                yhat_step = float(preds[0])
                lower_step = float(intervals[0, 0, 0])
                upper_step = float(intervals[0, 1, 0])
            else:
                yhat_step = float(self._regressor.predict(X_current)[0])
                alpha = self.config.alpha
                lower_q = 100 * (alpha / 2.0)
                upper_q = 100 * (1.0 - alpha / 2.0)
                q_low, q_high = np.percentile(residuals, [lower_q, upper_q])
                lower_step = yhat_step + float(q_low)
                upper_step = yhat_step + float(q_high)

            yhat_list.append(yhat_step)
            lower_list.append(lower_step)
            upper_list.append(upper_step)
            ds_list.append(current_date)

            df_all = pd.concat(
                [df_all, pd.DataFrame({"ds": [current_date], "y": [yhat_step]})],
                ignore_index=True,
            )

        return (
            np.asarray(yhat_list, dtype=float),
            np.asarray(lower_list, dtype=float),
            np.asarray(upper_list, dtype=float),
            ds_list,
        )

    def save(self, path: Path) -> None:
        import pickle

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            pickle.dump(self, f)
        logger.info("Saved LGBMForecaster to %s", path)

    @classmethod
    def load(cls, path: Path) -> "LGBMForecaster":
        import pickle

        path = Path(path)
        with path.open("rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__} instance.")
        logger.info("Loaded LGBMForecaster from %s", path)
        return obj

    def predict(self, future_df: pd.DataFrame, horizon: int = FORECAST_HORIZON_DAYS) -> pd.DataFrame:
        if self._history_df is None:
            raise RuntimeError("LGBMForecaster has not been fitted yet.")

        df_future = future_df.copy()
        df_future["ds"] = pd.to_datetime(df_future["ds"])
        df_future = df_future.sort_values("ds")

        logger.info("LGBMForecaster predicting for horizon=%d", horizon)

        history_df = self._history_df.copy()
        yhat, lower, upper, ds_list = self._predict_stepwise(history_df, horizon=horizon)

        out = pd.DataFrame(
            {
                "ds": ds_list,
                "yhat": yhat,
                "yhat_lower": lower,
                "yhat_upper": upper,
            }
        )
        return out