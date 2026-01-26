from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Mapping, Tuple

import numpy as np
import pandas as pd

from ..config import INVENTORY_DEFAULTS
from ..logging_utils import get_logger
from .policies import InventoryInputs, build_policy
from .scenarios import generate_scenario_policies

logger = get_logger(__name__)


def _summarise_forecast(forecast_df: pd.DataFrame) -> Tuple[float, float, float]:
    if "yhat" not in forecast_df.columns:
        raise ValueError("forecast_df must contain a 'yhat' column.")
    yhat = forecast_df["yhat"].astype(float).to_numpy()
    if yhat.size == 0:
        raise ValueError("forecast_df is empty; cannot compute inventory inputs.")
    avg_daily = float(np.mean(yhat))
    std_daily = float(np.std(yhat, ddof=1)) if yhat.size > 1 else 0.0
    annual = float(avg_daily * 365.0)
    logger.info(
        "Forecast summary: avg_daily=%.3f, std_daily=%.3f, annual=%.3f",
        avg_daily,
        std_daily,
        annual,
    )
    return avg_daily, std_daily, annual


def optimize_inventory(
    forecast_df: pd.DataFrame,
    lead_time_days: float | None = None,
    order_cost: float | None = None,
    holding_cost_per_unit_year: float | None = None,
    holding_cost_pct: float | None = None,
    unit_cost: float = 1.0,
    service_level: float | None = None,
) -> Dict[str, Any]:
    """
    Compute EOQ, reorder point, and safety stock given a demand forecast and
    basic business parameters.

    Parameters
    ----------
    forecast_df:
        DataFrame with at least a 'yhat' column (forecasted daily demand).
    lead_time_days:
        Lead time in days. If None, uses project default.
    order_cost:
        Ordering cost per order. If None, uses project default.
    holding_cost_per_unit_year:
        Holding cost per unit per year. If None, will be derived from
        holding_cost_pct * unit_cost or project defaults.
    holding_cost_pct:
        Fraction of unit cost charged per year as holding cost.
    unit_cost:
        Unit purchase cost (used with holding_cost_pct when needed).
    service_level:
        Target cycle service level (0-1). If None, uses project default.

    Returns
    -------
    dict
        Dictionary containing the optimized policy, baseline comparison, and
        scenario table (as a list of dicts).
    """
    lt_days = float(lead_time_days if lead_time_days is not None else INVENTORY_DEFAULTS["lead_time_days"])
    svc_level = float(service_level if service_level is not None else INVENTORY_DEFAULTS["service_level"])
    order_cost_val = float(order_cost if order_cost is not None else INVENTORY_DEFAULTS["ordering_cost"])

    if holding_cost_per_unit_year is not None:
        H = float(holding_cost_per_unit_year)
    else:
        pct = float(holding_cost_pct if holding_cost_pct is not None else INVENTORY_DEFAULTS["holding_cost_pct"])
        H = pct * float(unit_cost)

    avg_daily, std_daily, annual = _summarise_forecast(forecast_df)

    inputs = InventoryInputs(
        avg_daily_demand=avg_daily,
        std_daily_demand=std_daily,
        lead_time_days=lt_days,
        annual_demand=annual,
        order_cost=order_cost_val,
        holding_cost_per_unit_year=H,
        service_level=svc_level,
    )

    optimized_policy = build_policy(inputs)

    # Simple baseline: order quantity equal to average demand over 30 days,
    # no safety stock.
    baseline_Q = max(1.0, avg_daily * 30.0)
    baseline_safety_stock = 0.0
    baseline_rop = avg_daily * lt_days + baseline_safety_stock

    from .costing import compute_cost_breakdown

    baseline_cost = compute_cost_breakdown(
        annual_demand=annual,
        order_quantity=baseline_Q,
        safety_stock=baseline_safety_stock,
        order_cost=order_cost_val,
        holding_cost_per_unit=H,
    )

    baseline_policy = {
        "order_quantity": baseline_Q,
        "reorder_point": baseline_rop,
        "safety_stock": baseline_safety_stock,
        "expected_cycle_stock": baseline_Q / 2.0,
        "days_of_cover": baseline_Q / max(1e-8, avg_daily),
        **baseline_cost.to_dict(),
    }

    opt_total = optimized_policy.cost_breakdown["total_cost_annual"]
    base_total = baseline_policy["total_cost_annual"]
    if base_total > 0.0:
        cost_diff_pct = 100.0 * (opt_total - base_total) / base_total
    else:
        cost_diff_pct = 0.0

    scenario_df = generate_scenario_policies(inputs)
    scenarios_list = scenario_df.to_dict(orient="records")

    result: Dict[str, Any] = {
        "inputs": asdict(inputs),
        "optimized_policy": optimized_policy.to_dict(),
        "baseline_policy": baseline_policy,
        "cost_improvement_pct_vs_baseline": cost_diff_pct,
        "scenarios": scenarios_list,
    }
    logger.info("Inventory optimization result prepared.")
    return result