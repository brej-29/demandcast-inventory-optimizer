# Metrics and Targets

This document describes the primary metrics and rough target ranges for the
DemandCast project. These are **guiding values**, not hard guarantees.

## Forecasting metrics

Baseline metrics for time series forecasts:

- **RMSE (Root Mean Squared Error)**
  - Sensitive to large errors.
  - Useful for comparing models on the original scale of the target.
- **MAPE (Mean Absolute Percentage Error)**
  - Expressed as a percentage.
  - Less meaningful when true values can be near zero.
- **sMAPE (Symmetric Mean Absolute Percentage Error)**
  - Addresses some issues with MAPE by symmetrizing the denominator.

These metrics are implemented in `src/demandcast/evaluation/metrics.py`.

### Initial targets (subject to revision)

Targets will depend on the specific forecast horizon, aggregation level, and
business constraints. As a starting point for the competition dataset:

- Aim for **sMAPE below ~20%** on a reasonably strict validation setup.
- Track RMSE and MAPE alongside sMAPE to understand scale and relative error.

Targets should be revisited as:

- The modeling approach matures.
- Additional constraints (e.g., per-store or per-item guarantees) are introduced.

## Inventory-related metrics

Once inventory optimization is implemented, we will monitor:

- **Service level** – fraction of demand fulfilled without stockouts.
- **Fill rate** – fraction of demand volume satisfied without backorders.
- **Stockout count / rate** – number or proportion of periods with stockouts.
- **Inventory turns / holding cost** – proxy for capital efficiency.
- **Ordering cost** – cost associated with placing orders (per-order overhead).

### Inventory targets (initial ideas)

- Service level targets in the **90–99%** range depending on item criticality.
- Balance between holding cost and stockout risk should be documented explicitly
  for each scenario or segment.

## Logging and observability

- All core workflows should log:
  - Dataset versions and filters (dates, stores, items).
  - Model configuration and random seeds.
  - Key evaluation metrics.
- Logs should be sufficient to reconstruct how a given metric was produced
  without needing to dig into notebooks.

These practices are intended to make experimentation repeatable and decisions
traceable over time.