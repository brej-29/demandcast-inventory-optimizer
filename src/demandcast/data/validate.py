from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict

import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class SeriesDiagnostics:
    n_rows: int
    ds_start: str
    ds_end: str
    is_monotonic: bool
    n_duplicates: int
    n_missing_y: int
    missing_y_fraction: float
    n_negative_y: int

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def compute_basic_series_diagnostics(df: pd.DataFrame) -> SeriesDiagnostics:
    if "ds" not in df.columns or "y" not in df.columns:
        raise ValueError("Series DataFrame must contain 'ds' and 'y' columns.")

    series = df.copy()
    series["ds"] = pd.to_datetime(series["ds"])
    series = series.sort_values("ds")

    n_rows = len(series)
    ds_start = series["ds"].min().isoformat() if n_rows else ""
    ds_end = series["ds"].max().isoformat() if n_rows else ""
    is_monotonic = series["ds"].is_monotonic_increasing
    n_duplicates = int(series.duplicated(subset=["ds"]).sum())
    n_missing_y = int(series["y"].isna().sum())
    missing_fraction = float(series["y"].isna().mean()) if n_rows else 0.0
    n_negative_y = int((series["y"] < 0).sum())

    logger.info(
        "Series diagnostics: n_rows=%d, ds_start=%s, ds_end=%s, missing_y=%d, "
        "negative_y=%d, duplicates=%d",
        n_rows,
        ds_start,
        ds_end,
        n_missing_y,
        n_negative_y,
        n_duplicates,
    )

    return SeriesDiagnostics(
        n_rows=n_rows,
        ds_start=ds_start,
        ds_end=ds_end,
        is_monotonic=is_monotonic,
        n_duplicates=n_duplicates,
        n_missing_y=n_missing_y,
        missing_y_fraction=missing_fraction,
        n_negative_y=n_negative_y,
    )


def validate_series_df(df: pd.DataFrame) -> SeriesDiagnostics:
    diagnostics = compute_basic_series_diagnostics(df)

    if diagnostics.n_rows == 0:
        raise ValueError("Series DataFrame is empty after preprocessing.")

    if diagnostics.n_duplicates > 0:
        logger.warning("Found %d duplicate ds values in series.", diagnostics.n_duplicates)

    if diagnostics.n_missing_y > 0:
        logger.warning(
            "Found %d missing y values in series (%.4f fraction).",
            diagnostics.n_missing_y,
            diagnostics.missing_y_fraction,
        )

    if diagnostics.n_negative_y > 0:
        logger.warning("Found %d negative y values in series.", diagnostics.n_negative_y)

    return diagnostics