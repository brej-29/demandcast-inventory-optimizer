from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class CostBreakdown:
    annual_demand: float
    eoq: float
    ordering_cost_annual: float
    holding_cost_annual: float
    total_cost_annual: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "annual_demand": self.annual_demand,
            "eoq": self.eoq,
            "ordering_cost_annual": self.ordering_cost_annual,
            "holding_cost_annual": self.holding_cost_annual,
            "total_cost_annual": self.total_cost_annual,
        }


def compute_eoq(annual_demand: float, order_cost: float, holding_cost_per_unit: float) -> float:
    """
    Economic order quantity (EOQ) formula:

        Q* = sqrt(2 * D * S / H)

    where:
        D = annual demand
        S = ordering cost per order
        H = holding cost per unit per year
    """
    D = max(0.0, float(annual_demand))
    S = max(0.0, float(order_cost))
    H = max(1e-8, float(holding_cost_per_unit))

    eoq = (2.0 * D * S / H) ** 0.5
    logger.debug(
        "Computed EOQ with D=%.3f, S=%.3f, H=%.3f -> EOQ=%.3f",
        D,
        S,
        H,
        eoq,
    )
    return eoq


def compute_ordering_cost_annual(annual_demand: float, order_quantity: float, order_cost: float) -> float:
    D = max(0.0, float(annual_demand))
    Q = max(1e-8, float(order_quantity))
    S = max(0.0, float(order_cost))
    return (D / Q) * S


def compute_holding_cost_annual(
    order_quantity: float,
    safety_stock: float,
    holding_cost_per_unit: float,
) -> float:
    Q = max(0.0, float(order_quantity))
    SS = max(0.0, float(safety_stock))
    H = max(0.0, float(holding_cost_per_unit))
    return (Q / 2.0 + SS) * H


def compute_cost_breakdown(
    annual_demand: float,
    order_quantity: float,
    safety_stock: float,
    order_cost: float,
    holding_cost_per_unit: float,
) -> CostBreakdown:
    ordering_cost = compute_ordering_cost_annual(annual_demand, order_quantity, order_cost)
    holding_cost = compute_holding_cost_annual(order_quantity, safety_stock, holding_cost_per_unit)
    total_cost = ordering_cost + holding_cost
    breakdown = CostBreakdown(
        annual_demand=annual_demand,
        eoq=order_quantity,
        ordering_cost_annual=ordering_cost,
        holding_cost_annual=holding_cost,
        total_cost_annual=total_cost,
    )
    logger.debug("Cost breakdown: %s", breakdown.to_dict())
    return breakdown