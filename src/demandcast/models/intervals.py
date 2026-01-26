from __future__ import annotations

from typing import Any, Optional

import numpy as np
from ..logging_utils import get_logger

logger = get_logger(__name__)

try:  # pragma: no cover - optional dependency
    from mapie.time_series import MapieTimeSeriesRegressor
    from mapie.subsample import BlockBootstrap

    _MAPIE_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    MapieTimeSeriesRegressor = None  # type: ignore
    BlockBootstrap = None  # type: ignore
    _MAPIE_AVAILABLE = False


def build_mapie_timeseries_regressor(
    base_estimator: Any,
    alpha: float = 0.1,
    random_state: int = 42,
) -> Optional[Any]:
    """
    Build a MAPIE time-series regressor using EnbPI if MAPIE is available.

    Parameters
    ----------
    base_estimator:
        Any sklearn-like regressor implementing fit/predict.
    alpha:
        Miscoverage level (e.g. 0.1 for 90% intervals).
    random_state:
        Random seed for the underlying bootstrap.

    Returns
    -------
    MapieTimeSeriesRegressor or None
        If MAPIE is not installed, returns None and logs a warning.
    """
    if not _MAPIE_AVAILABLE:
        logger.warning(
            "MAPIE is not available; falling back to simple empirical intervals."
        )
        return None

    cv = BlockBootstrap(n_blocks=10, overlapping=True, random_state=random_state)
    mapie = MapieTimeSeriesRegressor(
        estimator=base_estimator,
        method="enbpi",
        cv=cv,
        n_jobs=-1,
        random_state=random_state,
    )
    logger.info(
        "Created MapieTimeSeriesRegressor with EnbPI (alpha=%.3f, random_state=%d)",
        alpha,
        random_state,
    )
    return mapie