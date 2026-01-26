from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from ..logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class ETSConfig:
    trend: Optional[str] = "add"
    seasonal: Optional[str] = "add"
    seasonal_periods: int = 7
    damped_trend: bool = False
    alpha: float = 0.1  # 90% intervals


class ETSModel:
    def __init__(self, config: Optional[ETSConfig] = None) -> None:
        self.config = config or ETSConfig()
        self._fitted_model: Optional[ExponentialSmoothing] = None
        self._results = None

    def fit(self, series_df: pd.DataFrame) -> "ETSModel":
        df = series_df.copy()
        if "ds" not in df.columns or "y" not in df.columns:
            raise ValueError("Series DataFrame must contain 'ds' and 'y' columns.")

        df = df.sort_values("ds")
        y = df["y"].astype(float).to_numpy()

        logger.info(
            "Fitting ETS model with trend=%s, seasonal=%s, seasonal_periods=%d",
            self.config.trend,
            self.config.seasonal,
            self.config.seasonal_periods,
        )
        self._fitted_model = ExponentialSmoothing(
            y,
            trend=self.config.trend,
            seasonal=self.config.seasonal,
            seasonal_periods=self.config.seasonal_periods,
            damped_trend=self.config.damped_trend,
        )
        self._results = self._fitted_model.fit()
        return self

    def predict(self, future_df: pd.DataFrame, horizon: int) -> pd.DataFrame:
        if self._results is None:
            raise RuntimeError("ETS model has not been fitted yet.")

        alpha = self.config.alpha
        logger.info("Generating ETS forecasts for horizon=%d with alpha=%.3f", horizon, alpha)

        yhat = self._results.forecast(steps=horizon)
        sigma_hat = np.std(self._results.resid, ddof=1) if len(self._results.resid) > 1 else 0.0
        z = 1.0 / alpha if alpha > 0 else 1.96  # rough fallback if needed

        lower = yhat - z * sigma_hat
        upper = yhat + z * sigma_hat

        ds = pd.to_datetime(future_df["ds"]).sort_values().head(horizon).reset_index(drop=True)
        out = pd.DataFrame(
            {
                "ds": ds,
                "yhat": np.asarray(yhat)[:horizon],
                "yhat_lower": np.asarray(lower)[:horizon],
                "yhat_upper": np.asarray(upper)[:horizon],
            }
        )
        return out