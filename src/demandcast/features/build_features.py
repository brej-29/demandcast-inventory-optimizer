from typing import Any

import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


def build_time_series_features(df: pd.DataFrame, *args: Any, **kwargs: Any) -> pd.DataFrame:
    """
    Placeholder for time series feature engineering.

    For now this function returns a shallow copy of the input DataFrame and logs
    the call. Feature engineering (lags, rolling windows, calendar features, etc.)
    will be implemented in a later step.
    """
    logger.info(
        "build_time_series_features called with %d rows and %d columns",
        len(df),
        len(df.columns),
    )
    _ = args, kwargs  # currently unused
    return df.copy()