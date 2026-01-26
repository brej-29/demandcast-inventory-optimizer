from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple, Type

import numpy as np
import pandas as pd

from ..config import METRIC_NAMES
from ..logging_utils import get_logger
from .metrics import compute_all_metrics

logger = get_logger(__name__)


@dataclass
class RollingBacktestSettings:
    initial_train_days: int
    step_days: int
    horizon_days: int
    n_folds: int

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)


@dataclass
class BacktestFoldResult:
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    metrics: Mapping[str, float]


def _get_train_test_splits(
    series: pd.DataFrame,
    settings: RollingBacktestSettings,
) -> List[Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    ds = pd.to_datetime(series["ds"])
    start = ds.min()
    end = ds.max()

    splits: List[Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]] = []
    for k in range(settings.n_folds):
        train_end = start + pd.Timedelta(days=settings.initial_train_days + k * settings.step_days)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.Timedelta(days=settings.horizon_days - 1)

        if test_end > end:
            break

        splits.append((start, train_end, test_start, test_end))

    logger.info("Generated %d backtest splits.", len(splits))
    return splits


def rolling_origin_backtest(
    series: pd.DataFrame,
    model_class: Callable[[], Any],
    settings: RollingBacktestSettings,
) -> Tuple[pd.DataFrame, List[BacktestFoldResult]]:
    series_local = series.sort_values("ds").reset_index(drop=True)
    splits = _get_train_test_splits(series_local, settings)

    all_preds: List[pd.DataFrame] = []
    fold_results: List[BacktestFoldResult] = []

    for fold_idx, (train_start, train_end, test_start, test_end) in enumerate(splits, start=1):
        logger.info(
            "Backtest fold %d: train=%s..%s, test=%s..%s",
            fold_idx,
            train_start.date(),
            train_end.date(),
            test_start.date(),
            test_end.date(),
        )

        train_mask = (series_local["ds"] >= train_start) & (series_local["ds"] <= train_end)
        test_mask = (series_local["ds"] >= test_start) & (series_local["ds"] <= test_end)

        train_df = series_local.loc[train_mask].copy()
        test_df = series_local.loc[test_mask].copy()

        if train_df.empty or test_df.empty:
            logger.warning(
                "Skipping fold %d because train or test set is empty (train=%d, test=%d).",
                fold_idx,
                len(train_df),
                len(test_df),
            )
            continue

        model = model_class()
        model = model.fit(train_df)

        preds = model.predict(test_df, horizon=settings.horizon_days)
        required_cols = {"ds", "yhat"}
        missing = required_cols - set(preds.columns)
        if missing:
            raise ValueError(f"Model predictions missing required columns: {missing}")

        merged = pd.merge(
            test_df[["ds", "y"]],
            preds,
            on="ds",
            how="left",
            suffixes=("", "_pred"),
        )
        merged["fold"] = fold_idx

        all_preds.append(merged)

        y_true = merged["y"].to_numpy(dtype=float)
        y_pred = merged["yhat"].to_numpy(dtype=float)
        y_lower = (
            merged["yhat_lower"].to_numpy(dtype=float)
            if "yhat_lower" in merged.columns
            else None
        )
        y_upper = (
            merged["yhat_upper"].to_numpy(dtype=float)
            if "yhat_upper" in merged.columns
            else None
        )

        metrics = compute_all_metrics(y_true, y_pred, y_lower, y_upper)
        fold_results.append(
            BacktestFoldResult(
                train_start=train_start.isoformat(),
                train_end=train_end.isoformat(),
                test_start=test_start.isoformat(),
                test_end=test_end.isoformat(),
                metrics=metrics,
            )
        )

    if not all_preds:
        raise RuntimeError("No valid backtest folds were produced.")

    preds_df = pd.concat(all_preds, ignore_index=True)
    preds_df = preds_df.sort_values(["fold", "ds"]).reset_index(drop=True)

    return preds_df, fold_results


def backtest_model_class(
    series: pd.DataFrame,
    model_class: Callable[[], Any],
    settings: RollingBacktestSettings,
) -> Tuple[pd.DataFrame, Mapping[str, float], List[BacktestFoldResult]]:
    preds_df, fold_results = rolling_origin_backtest(series, model_class, settings)

    agg_metrics: Dict[str, float] = {}
    for metric_name in METRIC_NAMES:
        values = [fr.metrics.get(metric_name) for fr in fold_results]
        values = [v for v in values if v is not None]
        if values:
            agg_metrics[metric_name] = float(np.mean(values))

    if "coverage" in fold_results[0].metrics:
        coverages = [fr.metrics.get("coverage") for fr in fold_results if "coverage" in fr.metrics]
        coverages = [c for c in coverages if c is not None]
        if coverages:
            agg_metrics["coverage"] = float(np.mean(coverages))

    if "mean_interval_width" in fold_results[0].metrics:
        widths = [
            fr.metrics.get("mean_interval_width")
            for fr in fold_results
            if "mean_interval_width" in fr.metrics
        ]
        widths = [w for w in widths if w is not None]
        if widths:
            agg_metrics["mean_interval_width"] = float(np.mean(widths))

    logger.info("Aggregate backtest metrics: %s", agg_metrics)
    return preds_df, agg_metrics, fold_results