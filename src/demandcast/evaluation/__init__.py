"""Evaluation metrics and utilities for DemandCast."""

from .metrics import (
    compute_all_metrics,
    compute_metrics_from_dataframe,
    coverage_fraction,
    mae,
    mape,
    mean_interval_width,
    rmse,
    smape,
    wape,
)

from .backtest import (
    RollingBacktestSettings,
    backtest_model_class,
    rolling_origin_backtest,
)

__all__ = [
    "rmse",
    "mae",
    "mape",
    "smape",
    "wape",
    "coverage_fraction",
    "mean_interval_width",
    "compute_all_metrics",
    "compute_metrics_from_dataframe",
    "RollingBacktestSettings",
    "rolling_origin_backtest",
    "backtest_model_class",
]