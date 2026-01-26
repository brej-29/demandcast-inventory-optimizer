from pathlib import Path
from typing import Optional

import pandas as pd

from ..config import (
    DATA_RAW_DIR,
    DEFAULT_ITEM_ID,
    DEFAULT_SERIES_MODE,
    DEFAULT_STORE_ID,
    KAGGLE_COMPETITION,
    RAW_TRAIN_FILENAME,
    RESAMPLE_FREQ,
)
from ..logging_utils import get_logger

logger = get_logger(__name__)


def locate_kaggle_train_csv() -> Path:
    csv_path = DATA_RAW_DIR / RAW_TRAIN_FILENAME
    if not csv_path.exists():
        logger.error("Training data not found at %s", csv_path)
        raise FileNotFoundError(
            f"Expected training data at {csv_path}.\n"
            f"Download it using the Kaggle CLI, for example:\n\n"
            f"  kaggle competitions download -c {KAGGLE_COMPETITION} -p data/raw\n\n"
            "or run one of the helper scripts:\n"
            "  bash scripts/download_kaggle_competition.sh\n"
            "  pwsh scripts/download_kaggle_competition.ps1"
        )
    return csv_path


def load_kaggle_train_df(path: Path) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        logger.error("Training CSV does not exist at %s", csv_path)
        raise FileNotFoundError(
            f"Training CSV not found at {csv_path}. "
            "Ensure you have downloaded the Kaggle competition files."
        )
    logger.info("Loading Kaggle train CSV from %s", csv_path)
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    required_cols = ["date", "store", "item", "sales"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in training data: {missing}. "
            f"Expected at least: {required_cols}"
        )
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    n_bad_dates = int(df["date"].isna().sum())
    if n_bad_dates > 0:
        logger.warning(
            "Coerced %d rows with invalid dates to NaT; these rows will be dropped.",
            n_bad_dates,
        )
    sales_raw = df["sales"]
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    n_new_nans = int(df["sales"].isna().sum() - sales_raw.isna().sum())
    if n_new_nans > 0:
        logger.warning(
            "Coerced %d non-numeric sales values to NaN; these rows will be dropped.",
            n_new_nans,
        )
    negative_mask = df["sales"] < 0
    n_negative = int(negative_mask.sum())
    if n_negative > 0:
        logger.warning(
            "Found %d rows with negative sales; setting these values to 0.", n_negative
        )
        df.loc[negative_mask, "sales"] = 0.0

    n_before = len(df)
    df = df.dropna(subset=["date", "sales"])
    n_dropped = n_before - len(df)
    if n_dropped > 0:
        logger.warning("Dropped %d rows with missing date or sales.", n_dropped)

    if not df.empty:
        date_min = df["date"].min()
        date_max = df["date"].max()
        n_stores = df["store"].nunique()
        n_items = df["item"].nunique()
        missing_pct = float(df["sales"].isna().mean() * 100.0)

        logger.info(
            "Loaded training data: %d rows, %d stores, %d items, date range %s -> %s",
            len(df),
            n_stores,
            n_items,
            date_min.date() if hasattr(date_min, "date") else date_min,
            date_max.date() if hasattr(date_max, "date") else date_max,
        )
        logger.info("Missing sales percentage after cleaning: %.3f%%", missing_pct)
    else:
        logger.warning("Training DataFrame is empty after cleaning.")

    return df


def build_target_series(
    df: pd.DataFrame,
    mode: str = DEFAULT_SERIES_MODE,
    store_id: int = DEFAULT_STORE_ID,
    item_id: int = DEFAULT_ITEM_ID,
    freq: str = RESAMPLE_FREQ,
    fill_missing: str = "zero",
) -> pd.DataFrame:
    mode = mode.lower()
    if mode not in ("single_sku", "aggregate_items", "aggregate_stores", "total"):
        raise ValueError(f"Unsupported series mode: {mode}")

    df_local = df.copy()
    df_local["date"] = pd.to_datetime(df_local["date"])

    if mode == "single_sku":
        mask = (df_local["store"] == store_id) & (df_local["item"] == item_id)
        subset = df_local.loc[mask]
        if subset.empty:
            raise ValueError(
                f"No data found for store={store_id}, item={item_id} in single_sku mode."
            )
        grouped = subset.groupby("date", as_index=False)["sales"].sum()
        grouped["store"] = store_id
        grouped["item"] = item_id
    elif mode == "aggregate_items":
        subset = df_local[df_local["store"] == store_id]
        if subset.empty:
            raise ValueError(f"No data found for store={store_id} in aggregate_items mode.")
        grouped = subset.groupby("date", as_index=False)["sales"].sum()
        grouped["store"] = store_id
    elif mode == "aggregate_stores":
        subset = df_local[df_local["item"] == item_id]
        if subset.empty:
            raise ValueError(f"No data found for item={item_id} in aggregate_stores mode.")
        grouped = subset.groupby("date", as_index=False)["sales"].sum()
        grouped["item"] = item_id
    elif mode == "total":
        grouped = df_local.groupby("date", as_index=False)["sales"].sum()
    else:  # defensive
        raise ValueError(f"Unsupported series mode: {mode}")

    grouped = grouped.rename(columns={"date": "ds", "sales": "y"})
    grouped["ds"] = pd.to_datetime(grouped["ds"])
    grouped = grouped.sort_values("ds")

    grouped = grouped.set_index("ds")
    if grouped.empty:
        raise ValueError("Grouped series is empty; cannot build target series.")

    full_index = pd.date_range(start=grouped.index.min(), end=grouped.index.max(), freq=freq)
    grouped = grouped.reindex(full_index)
    grouped.index.name = "ds"

    if fill_missing == "zero":
        grouped["y"] = grouped["y"].fillna(0.0)
    elif fill_missing == "ffill":
        grouped["y"] = grouped["y"].ffill()
        grouped["y"] = grouped["y"].fillna(0.0)
    elif fill_missing == "none":
        pass
    else:
        raise ValueError(f"Unsupported fill_missing strategy: {fill_missing}")

    if "store" in grouped.columns and grouped["store"].isna().any():
        grouped["store"] = grouped["store"].fillna(store_id)
    if "item" in grouped.columns and grouped["item"].isna().any():
        grouped["item"] = grouped["item"].fillna(item_id)

    series_df = grouped.reset_index()
    logger.info(
        "Built target series in mode=%s with %d rows (%s -> %s)",
        mode,
        len(series_df),
        series_df["ds"].min().date() if not series_df.empty else None,
        series_df["ds"].max().date() if not series_df.empty else None,
    )
    return series_df


def load_competition_train(path: Optional[Path] = None) -> pd.DataFrame:
    csv_path = Path(path) if path is not None else locate_kaggle_train_csv()
    return load_kaggle_train_df(csv_path)