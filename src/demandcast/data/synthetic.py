from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class DemoSeriesConfig:
    start: str = "2017-01-01"
    periods: int = 365 * 2
    freq: str = "D"
    base_level: float = 20.0
    trend_per_day: float = 0.01
    weekly_seasonality_amplitude: float = 5.0
    noise_std: float = 2.0
    random_seed: int = 123


def generate_demo_series(config: Optional[DemoSeriesConfig] = None) -> pd.DataFrame:
    """
    Generate a synthetic univariate demand series for demo / testing.

    Returns a DataFrame with columns:
        - ds: datetime
        - y: demand
        - store: int
        - item: int
    """
    if config is None:
        config = DemoSeriesConfig()

    rng = np.random.default_rng(config.random_seed)
    start = datetime.fromisoformat(config.start)
    dates = pd.date_range(start=start, periods=config.periods, freq=config.freq)

    t = np.arange(config.periods, dtype=float)
    trend = config.trend_per_day * t
    weekly = config.weekly_seasonality_amplitude * np.sin(2 * np.pi * t / 7.0)
    noise = rng.normal(0.0, config.noise_std, size=config.periods)

    y = config.base_level + trend + weekly + noise
    y = np.clip(y, a_min=0.0, a_max=None)

    df = pd.DataFrame({"ds": dates, "y": y})
    df["store"] = 1
    df["item"] = 1

    logger.info(
        "Generated demo series: start=%s, periods=%d, freq=%s",
        config.start,
        config.periods,
        config.freq,
    )
    return df