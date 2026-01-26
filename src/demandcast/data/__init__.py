"""Data access layer for DemandCast."""

from .load_data import (
    build_target_series,
    load_competition_train,
    load_kaggle_train_df,
    locate_kaggle_train_csv,
)

from .preprocess import load_processed_series, save_processed_series
from .synthetic import generate_demo_series
from .validate import (
    compute_basic_series_diagnostics,
    validate_series_df,
)

__all__ = [
    "build_target_series",
    "load_competition_train",
    "load_kaggle_train_df",
    "locate_kaggle_train_csv",
    "load_processed_series",
    "save_processed_series",
    "generate_demo_series",
    "compute_basic_series_diagnostics",
    "validate_series_df",
]