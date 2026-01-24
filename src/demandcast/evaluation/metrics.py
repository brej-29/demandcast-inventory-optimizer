from typing import Sequence

import numpy as np

from ..logging_utils import get_logger

logger = get_logger(__name__)


def _to_array(x: Sequence[float]) -> np.ndarray:
    return np.asarray(x, dtype=float)


def rmse(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """
    Root Mean Squared Error.

    Parameters
    ----------
    y_true, y_pred:
        Sequences of true and predicted values.

    Returns
    -------
    float
        RMSE value.
    """
    y_true_arr = _to_array(y_true)
    y_pred_arr = _to_array(y_pred)
    logger.debug("Computing RMSE for %d observations", y_true_arr.size)
    return float(np.sqrt(np.mean((y_true_arr - y_pred_arr) ** 2)))


def mape(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """
    Mean Absolute Percentage Error (in percent).

    Adds a small epsilon to the denominator to avoid division by zero.
    """
    y_true_arr = _to_array(y_true)
    y_pred_arr = _to_array(y_pred)
    eps = 1e-8
    logger.debug("Computing MAPE for %d observations", y_true_arr.size)
    return float(
        np.mean(np.abs((y_true_arr - y_pred_arr) / (y_true_arr + eps))) * 100.0
    )


def smape(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """
    Symmetric Mean Absolute Percentage Error (in percent).

    Uses the standard definition:
        sMAPE = 2 * |y - y_hat| / (|y| + |y_hat|)
    """
    y_true_arr = _to_array(y_true)
    y_pred_arr = _to_array(y_pred)
    eps = 1e-8
    logger.debug("Computing sMAPE for %d observations", y_true_arr.size)
    numerator = np.abs(y_pred_arr - y_true_arr)
    denominator = np.abs(y_true_arr) + np.abs(y_pred_arr) + eps
    return float(np.mean(2.0 * numerator / denominator) * 100.0)