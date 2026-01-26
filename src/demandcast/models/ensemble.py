from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Mapping, Optional

import numpy as np
import pandas as pd

from ..logging_utils import get_logger
from .arima_sarimax import ARIMASARIMAXModel
from .ets import ETSModel
from .lgbm import LGBMForecaster
from .prophet_fallback import ProphetFallbackModel

logger = get_logger(__name__)


BASE_MODEL_NAMES = ["sarimax", "ets", "prophet_or_fallback", "lgbm"]


@dataclass
class EnsembleConfig:
    weights: Dict[str, float] = field(default_factory=dict)
    interval_mode: str = "conservative"  # or "weighted_band"


class EnsembleForecaster:
    """
    Weighted ensemble over SARIMAX, ETS, Prophet-or-fallback, and LightGBM.

    Point forecasts are a weighted average of component forecasts. Intervals
    are either conservative (min of lowers, max of uppers) or a weighted band.
    """

    def __init__(self, config: Optional[EnsembleConfig] = None) -> None:
        self.config = config or EnsembleConfig()
        self.models: Dict[str, object] = {}
        self._fitted: bool = False

    @staticmethod
    def _default_equal_weights() -> Dict[str, float]:
        w = 1.0 / len(BASE_MODEL_NAMES)
        return {name: w for name in BASE_MODEL_NAMES}

    @staticmethod
    def normalize_weights(raw_weights: Mapping[str, float]) -> Dict[str, float]:
        positive_weights = {k: max(0.0, float(v)) for k, v in raw_weights.items()}
        total = float(sum(positive_weights.values()))
        if total <= 0.0:
            logger.warning(
                "All ensemble weights are non-positive; falling back to equal weights."
            )
            return EnsembleForecaster._default_equal_weights()
        normalized = {k: v / total for k, v in positive_weights.items()}
        return normalized

    def set_weights(self, weights: Mapping[str, float]) -> None:
        self.config.weights = self.normalize_weights(weights)
        logger.info("Ensemble weights set to: %s", self.config.weights)

    def fit(self, series_df: pd.DataFrame) -> "EnsembleForecaster":
        df = series_df.copy()
        if "ds" not in df.columns or "y" not in df.columns:
            raise ValueError("Series DataFrame must contain 'ds' and 'y' columns.")

        logger.info("Fitting ensemble base models on %d observations.", len(df))

        self.models = {
            "sarimax": ARIMASARIMAXModel(),
            "ets": ETSModel(),
            "prophet_or_fallback": ProphetFallbackModel(),
            "lgbm": LGBMForecaster(),
        }

        for name, model in self.models.items():
            logger.info("Fitting base model '%s' for ensemble.", name)
            model.fit(df)

        if not self.config.weights:
            self.config.weights = self._default_equal_weights()
        else:
            self.config.weights = self.normalize_weights(self.config.weights)

        self._fitted = True
        logger.info("Ensemble fitted with weights: %s", self.config.weights)
        return self

    def _collect_component_predictions(
        self,
        future_df: pd.DataFrame,
        horizon: int,
    ) -> Dict[str, pd.DataFrame]:
        preds: Dict[str, pd.DataFrame] = {}
        for name, model in self.models.items():
            logger.info("Generating predictions for component '%s' (horizon=%d)", name, horizon)
            preds_df = model.predict(future_df, horizon=horizon)
            required = {"ds", "yhat"}
            missing = required - set(preds_df.columns)
            if missing:
                raise ValueError(
                    f"Component model '{name}' predictions missing required columns: {missing}"
                )
            preds[name] = preds_df[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        return preds

    def _combine(
        self,
        component_preds: Dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        weights = self.config.weights or self._default_equal_weights()
        weights = self.normalize_weights(weights)

        ds = None
        for df in component_preds.values():
            ds = df["ds"]
            break
        if ds is None:
            raise RuntimeError("No component predictions supplied to ensemble.")

        yhat_comb = np.zeros(len(ds), dtype=float)
        ylow_stack: List[np.ndarray] = []
        yhigh_stack: List[np.ndarray] = []

        for name, df in component_preds.items():
            w = weights.get(name, 0.0)
            yhat_comb += w * df["yhat"].to_numpy(dtype=float)
            ylow_stack.append(df["yhat_lower"].to_numpy(dtype=float))
            yhigh_stack.append(df["yhat_upper"].to_numpy(dtype=float))

        ylow_stack_arr = np.vstack(ylow_stack)
        yhigh_stack_arr = np.vstack(yhigh_stack)

        if self.config.interval_mode == "weighted_band":
            ylow = np.zeros_like(yhat_comb)
            yhigh = np.zeros_like(yhat_comb)
            for idx, name in enumerate(component_preds.keys()):
                w = weights.get(name, 0.0)
                ylow += w * ylow_stack_arr[idx]
                yhigh += w * yhigh_stack_arr[idx]
        else:
            ylow = np.min(ylow_stack_arr, axis=0)
            yhigh = np.max(yhigh_stack_arr, axis=0)

        out = pd.DataFrame(
            {
                "ds": ds.values,
                "yhat": yhat_comb,
                "yhat_lower": ylow,
                "yhat_upper": yhigh,
            }
        )
        return out

    def predict(self, future_df: pd.DataFrame, horizon: int) -> pd.DataFrame:
        if not self._fitted:
            raise RuntimeError("EnsembleForecaster must be fitted before predicting.")

        df_future = future_df.copy()
        df_future["ds"] = pd.to_datetime(df_future["ds"])
        df_future = df_future.sort_values("ds")

        components = self._collect_component_predictions(df_future, horizon=horizon)
        combined = self._combine(components)
        return combined

    def save(self, path: Path) -> None:
        import pickle

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            pickle.dump(self, f)
        logger.info("Saved EnsembleForecaster to %s", path)

    @classmethod
    def load(cls, path: Path) -> "EnsembleForecaster":
        import pickle

        path = Path(path)
        with path.open("rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__} instance.")
        logger.info("Loaded EnsembleForecaster from %s", path)
        return obj

    def save_weights(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.config.weights, f, indent=2)
        logger.info("Saved ensemble weights to %s", path)