from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

from ..config import INVENTORY_DEFAULTS, artifact_config
from ..data.preprocess import load_processed_series
from ..inventory import optimize_inventory
from ..logging_utils import get_logger
from ..models import EnsembleForecaster
from ..paths import DEMO_DATA_DIR, ensure_directories

logger = get_logger(__name__)


def _load_series() -> Optional[pd.DataFrame]:
    try:
        df, _ = load_processed_series()
        return df
    except FileNotFoundError:
        demo_path = DEMO_DATA_DIR / "demo_series.csv"
        if demo_path.exists():
            df = pd.read_csv(demo_path)
            df["ds"] = pd.to_datetime(df["ds"])
            if "y" not in df.columns and "sales" in df.columns:
                df = df.rename(columns={"sales": "y"})
            return df
        return None


def _load_or_fit_ensemble(series_df: pd.DataFrame) -> EnsembleForecaster:
    models_dir = artifact_config.models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    ensemble_path = models_dir / "ensemble.pkl"
    if ensemble_path.exists():
        return EnsembleForecaster.load(ensemble_path)
    ensemble = EnsembleForecaster()
    ensemble.fit(series_df)
    ensemble.save(ensemble_path)
    return ensemble


def _get_default_forecast(series_df: pd.DataFrame) -> pd.DataFrame:
    ensemble = _load_or_fit_ensemble(series_df)
    last_ds = pd.to_datetime(series_df["ds"]).max()
    horizon = 90
    future_dates = pd.date_range(start=last_ds + pd.Timedelta(days=1), periods=horizon, freq="D")
    future_df = pd.DataFrame({"ds": future_dates})
    preds = ensemble.predict(future_df, horizon=horizon)
    return preds


def render_inventory() -> None:
    try:
        st.header("Inventory optimization")

        ensure_directories()

        series_df = _load_series()
        if series_df is None:
            st.warning(
                "No series data available and no demo assets found.\n\n"
                "Run the data preparation and training scripts first, or ensure "
                "`assets/demo/demo_series.csv` is present."
            )
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            lead_time_days = st.number_input(
                "Lead time (days)",
                min_value=1.0,
                max_value=60.0,
                value=float(INVENTORY_DEFAULTS["lead_time_days"]),
                step=1.0,
            )
            service_level = st.slider(
                "Service level (cycle)",
                min_value=0.80,
                max_value=0.99,
                value=float(INVENTORY_DEFAULTS["service_level"]),
                step=0.01,
            )

        with col2:
            ordering_cost = st.number_input(
                "Ordering cost per order",
                min_value=0.0,
                max_value=1000.0,
                value=float(INVENTORY_DEFAULTS["ordering_cost"]),
                step=1.0,
            )
            holding_cost_pct = st.number_input(
                "Holding cost (% of unit cost per year)",
                min_value=0.0,
                max_value=1.0,
                value=float(INVENTORY_DEFAULTS["holding_cost_pct"]),
                step=0.01,
            )

        with col3:
            unit_cost = st.number_input(
                "Unit cost",
                min_value=0.0,
                max_value=1000.0,
                value=10.0,
                step=1.0,
            )

        mode = st.radio(
            "Scenario preset",
            options=["balanced", "conservative", "aggressive", "custom"],
            index=0,
            horizontal=True,
        )

        if mode != "custom":
            if mode == "conservative":
                service_level = max(service_level, 0.98)
            elif mode == "aggressive":
                service_level = min(service_level, 0.90)

        if st.button("Compute inventory policy"):
            forecast_df = _get_default_forecast(series_df)
            result = optimize_inventory(
                forecast_df,
                lead_time_days=lead_time_days,
                order_cost=ordering_cost,
                holding_cost_pct=holding_cost_pct,
                unit_cost=unit_cost,
                service_level=service_level,
            )

            st.subheader("Optimized policy")
            st.json(result["optimized_policy"])

            st.subheader("Baseline policy (simple heuristic)")
            st.json(result["baseline_policy"])

            st.subheader("Scenarios")
            scen_df = pd.DataFrame(result["scenarios"])
            st.dataframe(scen_df)

        else:
            st.info(
                "Configure lead time, service level, and cost parameters, then click "
                "**Compute inventory policy** to see EOQ/ROP recommendations and scenarios."
            )

    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error while rendering Inventory page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the Inventory page. "
            "Check the logs for details."
        )