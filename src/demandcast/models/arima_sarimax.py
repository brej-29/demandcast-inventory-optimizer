from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults

from ..logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class ARIMASARIMAXConfig:
    order: tuple[int, int, int] = (1, 0, 0)
    seasonal_order: tuple[int, int, int, int] = (0, 0, 0, 0)
    enforce_stationarity: bool = True
    enforce_invertibility: bool = True
    freq: str = "D"
    alpha: float = 0.1  # 90% intervals by default


class ARIMASARIMAXModel:
    def __init__(self, config: Optional[ARIMASARIMAXConfig] = None) -> None:
        self.config = config or ARIMASARIMAXConfig()
        self._model: Optional[SARIMAX] = None
        self._results: Optional[SARIMAXResults] = None

    def fit(self, series_df: pd.DataFrame) -> "ARIMASARIMAXModel":
        df = series_df.copy()
        if "ds" not in df.columns or "y" not in df.columns:
            raise ValueError("Series DataFrame must contain 'ds' and 'y' columns.")

        df = df.sort_values("ds")
        y = df["y"].astype(float).to_numpy()

        logger.info(
            "Fitting SARIMAX model with order=%s, seasonal_order=%s on %d observations",
            self.config.order,
            self.config.seasonal_order,
            len(y),
        )

        self._model = SARIMAX(
            y,
            order=self.config.order,
            seasonal_order=self.config.seasonal_order,
            enforce_stationarity=self.config.enforce_stationarity,
            enforce_invertibility=self.config.enforce_invertibility,
        )
        self._results = self._model.fit(disp=False)
        return self

    def predict(self, future_df: pd.DataFrame, horizon: int) -> pd.DataFrame:
        if self._results is None:
            raise RuntimeError("Model has not been fitted yet.")

        last_index = len(self._results.data.endog) - 1
        start = last_index + 1
        end = last_index + horizon

        alpha = self.config.alpha
        logger.info(
            "Generating SARIMAX forecasts for horizon=%d with alpha=%.3f",
            horizon,
            alpha,
        )
        forecast_res = self._results.get_forecast(steps=horizon)
        yhat = forecast_res.predicted_mean
        conf_int = forecast_res.conf_int(alpha=alpha)

        ds = pd.to_datetime(future_df["ds"]).sort_values().head(horizon).reset_index(drop=True)

        if isinstance(conf_int, pd.DataFrame):
            lower = conf_int.iloc[:, 0].to_numpy()
            upper = conf_int.iloc[:, 1].to_numpy()
        else:
            lower = conf_int[:, 0]
            upper = conf_int[:, 1]

        out = pd.DataFrame(
            {
                "ds": ds,
                "yhat": np.asarray(yhat)[:horizon],
                "yhat_lower": np.asarray(lower)[:horizon],
                "yhat_upper": np.asarray(upper)[:horizon],
            }
        )
        return out

    def get_state(self) -> Dict[str, Any]:
        if self._results is None:
            raise RuntimeError("Model has not been fitted yet.")
        return {"params": self._results.params.tolist()}

    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "ARIMASARIMAXModel":
        model = cls()
        _ = state
        return model