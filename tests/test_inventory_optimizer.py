import pandas as pd

from demandcast.inventory import optimize_inventory


def _simple_forecast() -> pd.DataFrame:
    ds = pd.date_range(start="2021-01-01", periods=30, freq="D")
    yhat = pd.Series(range(20, 50), index=ds)
    return pd.DataFrame({"ds": ds, "yhat": yhat})


def test_eoq_monotonicity() -> None:
    forecast_df = _simple_forecast()

    res_low_demand = optimize_inventory(
        forecast_df.assign(yhat=lambda df: df["yhat"] / 2.0),
        lead_time_days=7,
        order_cost=50.0,
        holding_cost_pct=0.2,
        unit_cost=10.0,
        service_level=0.95,
    )
    res_high_demand = optimize_inventory(
        forecast_df.assign(yhat=lambda df: df["yhat"] * 2.0),
        lead_time_days=7,
        order_cost=50.0,
        holding_cost_pct=0.2,
        unit_cost=10.0,
        service_level=0.95,
    )

    eoq_low = res_low_demand["optimized_policy"]["order_quantity"]
    eoq_high = res_high_demand["optimized_policy"]["order_quantity"]
    assert eoq_high > eoq_low


def test_safety_stock_increases_with_service_level() -> None:
    forecast_df = _simple_forecast()

    res_low = optimize_inventory(
        forecast_df,
        lead_time_days=7,
        order_cost=50.0,
        holding_cost_pct=0.2,
        unit_cost=10.0,
        service_level=0.90,
    )
    res_high = optimize_inventory(
        forecast_df,
        lead_time_days=7,
        order_cost=50.0,
        holding_cost_pct=0.2,
        unit_cost=10.0,
        service_level=0.99,
    )

    ss_low = res_low["optimized_policy"]["safety_stock"]
    ss_high = res_high["optimized_policy"]["safety_stock"]
    assert ss_high > ss_low


def test_reorder_point_not_below_mean_demand_during_lead_time() -> None:
    forecast_df = _simple_forecast()

    result = optimize_inventory(
        forecast_df,
        lead_time_days=7,
        order_cost=50.0,
        holding_cost_pct=0.2,
        unit_cost=10.0,
        service_level=0.95,
    )

    inputs = result["inputs"]
    avg_daily = inputs["avg_daily_demand"]
    lead_time = inputs["lead_time_days"]
    expected_demand_lead_time = avg_daily * lead_time
    rop = result["optimized_policy"]["reorder_point"]

    assert rop >= expected_demand_lead_time