from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict

import numpy as np

from ..logging_utils import get_logger
from .costing import compute_cost_breakdown, compute_eoq
from .service_levels import get_z_for_service_level

logger = get_logger(__name__)


@dataclass
class InventoryInputs:
    avg_daily_demand: float
    std_daily_demand: float
    lead_time_days: float
    annual_demand: float
    order_cost: float
    holding_cost_per_unit_year: float
    service_level: float


@dataclass
class InventoryPolicy:
    order_quantity: float
    reorder_point: float
    safety_stock: float
    expected_cycle_stock: float
    days_of_cover: float
    cost_breakdown: Dict[str, float]

    def to_dict(self) -> Dict[str, float]:
        base = {
            "order_quantity": self.order_quantity,
            "reorder_point": self.reorder_point,
            "safety_stock": self.safety_stock,
            "expected_cycle_stock": self.expected_cycle_stock,
            "days_of_cover": self.days_of_cover,
        }
        base.update(self.cost_breakdown)
        return base


def compute_safety_stock_demand_only(
    avg_daily_demand: float,
    std_daily_demand: float,
    lead_time_days: float,
    service_level: float,
) -> float:
    z = get_z_for_service_level(service_level)
    sigma_L = std_daily_demand * (lead_time_days ** 0.5)
    ss = z * sigma_L
    logger.debug(
        "Computed safety stock (demand-only) with z=%.3f, std_daily=%.3f, L=%.3f -> SS=%.3f",
        z,
        std_daily_demand,
        lead_time_days,
        ss,
    )
    return max(0.0, ss)


def compute_reorder_point(avg_daily_demand: float, lead_time_days: float, safety_stock: float) -> float:
    demand_during_lead_time = avg_daily_demand * lead_time_days
    rop = demand_during_lead_time + safety_stock
    logger.debug(
        "Computed reorder point with avg_daily=%.3f, L=%.3f, SS=%.3f -> ROP=%.3f",
        avg_daily_demand,
        lead_time_days,
        safety_stock,
        rop,
    )
    return max(0.0, rop)


def build_policy(inputs: InventoryInputs) -> InventoryPolicy:
    eoq = compute_eoq(inputs.annual_demand, inputs.order_cost, inputs.holding_cost_per_unit_year)
    safety_stock = compute_safety_stock_demand_only(
        inputs.avg_daily_demand,
        inputs.std_daily_demand,
        inputs.lead_time_days,
        inputs.service_level,
    )
    reorder_point = compute_reorder_point(
        inputs.avg_daily_demand,
        inputs.lead_time_days,
        safety_stock,
    )
    expected_cycle_stock = eoq / 2.0
    days_of_cover = eoq / max(1e-8, inputs.avg_daily_demand)

    breakdown = compute_cost_breakdown(
        annual_demand=inputs.annual_demand,
        order_quantity=eoq,
        safety_stock=safety_stock,
        order_cost=inputs.order_cost,
        holding_cost_per_unit=inputs.holding_cost_per_unit_year,
    )

    policy = InventoryPolicy(
        order_quantity=eoq,
        reorder_point=reorder_point,
        safety_stock=safety_stock,
        expected_cycle_stock=expected_cycle_stock,
        days_of_cover=days_of_cover,
        cost_breakdown=breakdown.to_dict(),
    )
    logger.info("Built inventory policy: %s", policy.to_dict())
    return policy