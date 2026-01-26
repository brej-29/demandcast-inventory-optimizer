from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List

import pandas as pd

from ..logging_utils import get_logger
from .policies import InventoryInputs, build_policy

logger = get_logger(__name__)


@dataclass
class ScenarioConfig:
    name: str
    service_level: float
    lead_time_multiplier: float


SCENARIOS: Dict[str, ScenarioConfig] = {
    "conservative": ScenarioConfig(
        name="conservative",
        service_level=0.98,
        lead_time_multiplier=1.2,
    ),
    "balanced": ScenarioConfig(
        name="balanced",
        service_level=0.95,
        lead_time_multiplier=1.0,
    ),
    "aggressive": ScenarioConfig(
        name="aggressive",
        service_level=0.9,
        lead_time_multiplier=0.8,
    ),
}


def get_scenario_config(name: str) -> ScenarioConfig:
    key = name.lower()
    if key not in SCENARIOS:
        raise ValueError(f"Unknown scenario name: {name!r}")
    return SCENARIOS[key]


def generate_scenario_policies(
    base_inputs: InventoryInputs,
    scenario_names: Iterable[str] = ("conservative", "balanced", "aggressive"),
) -> pd.DataFrame:
    rows: List[Dict[str, float]] = []
    for name in scenario_names:
        cfg = get_scenario_config(name)
        inputs = InventoryInputs(
            avg_daily_demand=base_inputs.avg_daily_demand,
            std_daily_demand=base_inputs.std_daily_demand,
            lead_time_days=base_inputs.lead_time_days * cfg.lead_time_multiplier,
            annual_demand=base_inputs.annual_demand,
            order_cost=base_inputs.order_cost,
            holding_cost_per_unit_year=base_inputs.holding_cost_per_unit_year,
            service_level=cfg.service_level,
        )
        policy = build_policy(inputs)
        row = {"scenario": cfg.name}
        row.update(policy.to_dict())
        rows.append(row)

    df = pd.DataFrame(rows)
    logger.info("Generated %d inventory scenario policies.", len(df))
    return df