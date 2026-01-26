from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


def _to_array(x: Sequence[float]) -> np.ndarray:
    return np.asarray(x, dtype=float)


def rmse(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    y_true_arr = _to_array(y_true)
    y_pred_arr = _to_array(y_pred)
    logger.debug("Computing RMSE for %d observations", y_true_arr.size)
    return float(np.sqrt(np.mean((y_true_arr - y_pred_arr) ** 2)))


def mae(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    y_true_arr = _to_array(y_true)
    y_pred_arr = _to_array(y_pred)
    logger.debug("Computing MAE for %d observations", y_true_arr.size)
    return float(np.mean(np.abs(y_true_arr - y_pred_arr)))


def mape(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    y_true_arr = _to_array(y_true)
    y_pred_arr = _to_array(y_pred)
    eps = 1e-8
    logger.debug("Computing MAPE for %d observations", y_true_arr.size)
    return float(
        np.mean(np.abs((y_true_arr - y_pred_arr) / (y_true_arr + eps))) * 100.0
    )


def smape(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    y_true_arr = _to_array(y_true)
    y_pred_arr = _to_array(y_pred)
    eps = 1e-8
    logger.debug("Computing sMAPE for %d observations", y_true_arr.size)
    numerator = np.abs(y_pred_arr - y_true_arr)
    denominator = np.abs(y_true_arr) + np.abs(y_pred_arr) + eps
    return float(np.mean(2.0 * numerator / denominator) * 100.0)


def wape(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    y_true_arr = _to_array(y_true)
    y_pred_arr = _to_array(y_pred)
    denom = np.sum(np.abs(y_true_arr))
    if denom == 0.0:
        logger.debug("WAPE denominator is zero; returning 0.0")
        return 0.0
    num = np.sum(np.abs(y_true_arr - y_pred_arr))
    logger.debug("Computing WAPE for %d observations", y_true_arr.size)
    return float(num / denom * 100.0)


def coverage_fraction(
    y_true: Sequence[float],
    y_lower: Sequence[float],
    y_upper: Sequence[float],
) -> float:
    y_true_arr = _to_array(y_true)
    lower = _to_array(y_lower)
    upper = _to_array(y_upper)

    if y_true_arr.size == 0:
        return 0.0

    covered = (y_true_arr >= lower) & (y_true_arr <= upper)
    frac = float(np.mean(covered))
    logger.debug("Computed coverage fraction=%.4f over %d observations", frac, y_true_arr.size)
    return frac


def mean_interval_width(
    y_lower: Sequence[float],
    y_upper: Sequence[float],
) -> float:
    lower = _to_array(y_lower)
    upper = _to_array(y_upper)
    if lower.size == 0:
        return 0.0
    width = float(np.mean(upper - lower))
    logger.debug("Computed mean interval width=%.4f over %d observations", width, lower.size)
    return width


def compute_all_metrics(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    y_lower: Sequence[float] | None = None,
    y_upper: Sequence[float] | None = None,
) -> Mapping[str, float]:
    metrics: dict[str, float] = {
        "rmse": rmse(y_true, y_pred),
        "mae": mae(y_true, y_pred),
        "mape": mape(y_true, y_pred),
        "smape": smape(y_true, y_pred),
        "wape": wape(y_true, y_pred),
    }
    if y_lower is not None and y_upper is not None:
        metrics["coverage"] = coverage_fraction(y_true, y_lower, y_upper)
        metrics["mean_interval_width"] = mean_interval_width(y_lower, y_upper)
    return metrics


def compute_metrics_from_dataframe(df: pd.DataFrame) -> Mapping[str, float]:
    required = {"ds", "y", "yhat"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for metrics: {sorted(missing)}")

    y_true = df["y"].to_numpy(dtype=float)
    y_pred = df["yhat"].to_numpy(dtype=float)
    y_lower = df["yhat_lower"].to_numpy(dtype=float) if "yhat_lower" in df.columns else None
    y_upper = df["yhat_upper"].to_numpy(dtype=float) if "yhat_upper" in df.columns else None

    return compute_all_metrics(y_true, y_pred, y_lower, y_upper)