from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from statistics import NormalDist

from ..logging_utils import get_logger

logger = get_logger(__name__)


SERVICE_LEVEL_Z_TABLE: Dict[float, float] = {
    0.80: 0.8416,
    0.85: 1.0364,
    0.90: 1.2816,
    0.95: 1.6449,
    0.97: 1.8808,
    0.98: 2.0537,
    0.99: 2.3263,
    0.995: 2.5758,
}


def get_z_for_service_level(service_level: float) -> float:
    """
    Map a cycle service level in (0, 1) to a standard normal z-score.

    Uses NormalDist.inv_cdf when available, falling back to a small lookup
    table if necessary or if the input is out of range.
    """
    p = float(service_level)
    if p <= 0.0 or p >= 1.0:
        logger.warning("Service level %.4f is out of (0,1); clipping to [0.5, 0.999].", p)
        p = min(max(p, 0.5), 0.999)

    # Try analytical quantile first.
    try:
        z = NormalDist().inv_cdf(p)
        return float(z)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(
            "NormalDist.inv_cdf failed for p=%.4f (%s); falling back to lookup table.",
            p,
            exc,
        )

    # Fallback: use closest value from table.
    closest_p = min(SERVICE_LEVEL_Z_TABLE.keys(), key=lambda v: abs(v - p))
    z = SERVICE_LEVEL_Z_TABLE[closest_p]
    logger.info(
        "Using fallback z-score %.4f for service level %.4f (closest table p=%.3f)",
        z,
        p,
        closest_p,
    )
    return z