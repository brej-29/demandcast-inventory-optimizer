from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class FeatureConfig:
    lags: Tuple[int, ...] = (1, 7, 14, 28)
    rolling_windows: Tuple[int, ...] = (7, 28)
    add_calendar: bool = True


def build_time_features(df: pd.DataFrame) -> pd.DataFrame:
    if "ds" not in df.columns:
        raise ValueError("DataFrame must contain 'ds' column for time features.")

    df_local = df.copy()
    df_local["ds"] = pd.to_datetime(df_local["ds"])
    df_local["dow"] = df_local["ds"].dt.dayofweek
    df_local["doy"] = df_local["ds"].dt.dayofyear
    df_local["week"] = df_local["ds"].dt.isocalendar().week.astype(int)
    df_local["month"] = df_local["ds"].dt.month
    df_local["year"] = df_local["ds"].dt.year

    logger.debug("Built basic calendar features with shape %s", df_local.shape)
    return df_local


def build_lag_features(
    df: pd.DataFrame,
    target_col: str = "y",
    lags: Sequence[int] = (1, 7, 14, 28),
    rolling_windows: Sequence[int] = (7, 28),
) -> pd.DataFrame:
    if target_col not in df.columns:
        raise ValueError(f"DataFrame must contain '{target_col}' column for lag features.")

    df_local = df.copy()
    df_local = df_local.sort_values("ds")

    for lag in lags:
        col_name = f"{target_col}_lag_{lag}"
        df_local[col_name] = df_local[target_col].shift(lag)

    for window in rolling_windows:
        rolled = df_local[target_col].rolling(window=window)
        df_local[f"{target_col}_roll_mean_{window}"] = rolled.mean()
        df_local[f"{target_col}_roll_std_{window}"] = rolled.std(ddof=0)

    logger.debug(
        "Built lag/rolling features with lags=%s, windows=%s; shape=%s",
        lags,
        rolling_windows,
        df_local.shape,
    )
    return df_local


def build_time_series_features(
    df: pd.DataFrame,
    config: FeatureConfig | None = None,
) -> pd.DataFrame:
    if config is None:
        config = FeatureConfig()

    if "ds" not in df.columns:
        raise ValueError("Input DataFrame must contain 'ds' column.")
    if "y" not in df.columns:
        raise ValueError("Input DataFrame must contain 'y' column.")

    df_local = df.copy()
    df_local = df_local.sort_values("ds")

    if config.add_calendar:
        df_local = build_time_features(df_local)

    df_local = build_lag_features(
        df_local,
        target_col="y",
        lags=config.lags,
        rolling_windows=config.rolling_windows,
    )

    logger.info(
        "Built time series features: %d rows, %d columns",
        len(df_local),
        len(df_local.columns),
    )
    return df_local


def make_supervised_dataset(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    target_col: str = "y",
) -> Tuple[pd.DataFrame, pd.Series]:
    df_local = df.copy()
    missing_cols = [c for c in feature_cols if c not in df_local.columns]
    if missing_cols:
        raise ValueError(f"Missing feature columns in DataFrame: {missing_cols}")

    df_local = df_local.sort_values("ds")
    mask = df_local[list(feature_cols) + [target_col]].notna().all(axis=1)
    supervised = df_local.loc[mask].copy()

    X = supervised[list(feature_cols)]
    y = supervised[target_col].astype(float)

    logger.info(
        "Constructed supervised dataset: X shape=%s, y length=%d",
        X.shape,
        len(y),
    )
    return X, y


def get_default_feature_columns(df: pd.DataFrame) -> List[str]:
    exclude = {"ds", "y"}
    return [c for c in df.columns if c not in exclude]