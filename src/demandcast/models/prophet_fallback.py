from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from ..logging_utils import get_logger
from .arima_sarimax import ARIMASARIMAXConfig, ARIMASARIMAXModel

logger = get_logger(__name__)

try:
    from prophet import Prophet  # type: ignore

    _PROPHET_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    Prophet = None  # type: ignore
    _PROPHET_AVAILABLE = False


@dataclass
class ProphetConfig:
    interval_width: float = 0.9
    daily_seasonality: bool = True
    weekly_seasonality: bool = True
    yearly_seasonality: bool = True


class ProphetFallbackModel:
    """
    Use Prophet when available, otherwise fall back to a SARIMAX model.

    This keeps the pipeline robust on environments where Prophet cannot be
    installed (e.g. limited build images), while still taking advantage of
    Prophet when it is present.
    """

    def __init__(
        self,
        prophet_config: Optional[ProphetConfig] = None,
        sarimax_config: Optional[ARIMASARIMAXConfig] = None,
    ) -> None:
        self.prophet_config = prophet_config or ProphetConfig()
        self.sarimax_config = sarimax_config or ARIMASARIMAXConfig()
        self._use_prophet = _PROPHET_AVAILABLE
        self._model = None

        if self._use_prophet:
            logger.info("Prophet is available; ProphetFallbackModel will use Prophet.")
        else:
            logger.warning(
                "Prophet is not available; ProphetFallbackModel will fall back to SARIMAX."
            )

    def fit(self, series_df: pd.DataFrame) -> "ProphetFallbackModel":
        df = series_df.copy()
        if "ds" not in df.columns or "y" not in df.columns:
            raise ValueError("Series DataFrame must contain 'ds' and 'y' columns.")
        df = df.sort_values("ds")

        if self._use_prophet and Prophet is not None:
            logger.info("Fitting Prophet model on %d observations.", len(df))
            m = Prophet(
                interval_width=self.prophet_config.interval_width,
                daily_seasonality=self.prophet_config.daily_seasonality,
                weekly_seasonality=self.prophet_config.weekly_seasonality,
                yearly_seasonality=self.prophet_config.yearly_seasonality,
            )
            m.fit(df[["ds", "y"]].rename(columns={"ds": "ds", "y": "y"}))
            self._model = m
        else:
            logger.info("Fitting SARIMAX fallback model for ProphetFallbackModel.")
            sarimax = ARIMASARIMAXModel(config=self.sarimax_config)
            sarimax.fit(df)
            self._model = sarimax

        return self

    def predict(self, future_df: pd.DataFrame, horizon: int) -> pd.DataFrame:
        if self._model is None:
            raise RuntimeError("Model has not been fitted yet.")

        df_future = future_df.copy()
        df_future["ds"] = pd.to_datetime(df_future["ds"])
        df_future = df_future.sort_values("ds").head(horizon)

        if self._use_prophet and isinstance(self._model, Prophet):
            logger.info("Generating forecasts using Prophet for horizon=%d", horizon)
            future = df_future[["ds"]].rename(columns={"ds": "ds"})
            forecast = self._model.predict(future)
            out = pd.DataFrame(
                {
                    "ds": forecast["ds"],
                    "yhat": forecast["yhat"],
                    "yhat_lower": forecast["yhat_lower"],
                    "yhat_upper": forecast["yhat_upper"],
                }
            )
            return out
        else:
            logger.info("Generating forecasts using SARIMAX fallback for horizon=%d", horizon)
            if isinstance(self._model, ARIMASARIMAXModel):
                return self._model.predict(df_future, horizon=horizon)

            raise RuntimeError("Unsupported underlying model type for ProphetFallbackModel.")


__all__ = ["ProphetFallbackModel", "_PROPHET_AVAILABLE"]