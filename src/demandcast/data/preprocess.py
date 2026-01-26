from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from ..config import DATA_PROCESSED_DIR, data_config
from ..logging_utils import get_logger
from .validate import validate_series_df

logger = get_logger(__name__)


def get_default_processed_series_path() -> Path:
    return DATA_PROCESSED_DIR / data_config.processed_series_filename


def save_processed_series(df: pd.DataFrame, path: Optional[Path] = None) -> Path:
    if path is None:
        path = get_default_processed_series_path()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    diagnostics = validate_series_df(df)
    logger.info("Validated series before saving: %s", diagnostics.to_dict())

    try:
        df.to_parquet(path)
        logger.info("Saved processed series to %s (parquet)", path)
        return path
    except Exception as exc:
        logger.warning(
            "Failed to save series to parquet at %s (%s). Falling back to CSV.",
            path,
            exc,
        )
        csv_path = path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        logger.info("Saved processed series to %s (csv fallback)", csv_path)
        return csv_path


def _load_series_from_parquet_or_csv(path: Path) -> Tuple[pd.DataFrame, Path]:
    if path.with_suffix(".parquet").exists():
        candidate = path.with_suffix(".parquet")
        logger.info("Loading processed series from parquet at %s", candidate)
        df = pd.read_parquet(candidate)
        return df, candidate

    if path.with_suffix(".csv").exists():
        candidate = path.with_suffix(".csv")
        logger.info("Loading processed series from CSV at %s", candidate)
        df = pd.read_csv(candidate)
        return df, candidate

    raise FileNotFoundError(
        f"Could not find processed series at {path.with_suffix('.parquet')} "
        f"or {path.with_suffix('.csv')}"
    )


def load_processed_series(path: Optional[Path] = None) -> Tuple[pd.DataFrame, Path]:
    if path is None:
        path = get_default_processed_series_path()
    path = Path(path)

    df, actual_path = _load_series_from_parquet_or_csv(path)

    diagnostics = validate_series_df(df)
    logger.info("Loaded processed series from %s with diagnostics: %s", actual_path, diagnostics.to_dict())

    return df, actual_path