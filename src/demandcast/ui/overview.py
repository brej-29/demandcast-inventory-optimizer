from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from ..config import DATA_PROCESSED_DIR, data_config
from ..data.preprocess import get_default_processed_series_path, load_processed_series
from ..logging_utils import get_logger
from ..paths import DEMO_ARTIFACTS_DIR, DEMO_DATA_DIR

logger = get_logger(__name__)


def _load_series_summary() -> Optional[pd.DataFrame]:
    # Prefer processed Kaggle-based series if available.
    path = get_default_processed_series_path()
    if path.with_suffix(".parquet").exists() or path.with_suffix(".csv").exists():
        df, actual_path = load_processed_series(path)
        df["ds"] = pd.to_datetime(df["ds"])
        summary = {
            "source": "processed",
            "path": str(actual_path),
            "n_rows": len(df),
            "start": df["ds"].min(),
            "end": df["ds"].max(),
        }
        return pd.DataFrame([summary])

    # Fall back to demo series if present.
    demo_path = DEMO_DATA_DIR / "demo_series.csv"
    if demo_path.exists():
        df = pd.read_csv(demo_path)
        df["ds"] = pd.to_datetime(df["ds"])
        if "y" not in df.columns and "sales" in df.columns:
            df = df.rename(columns={"sales": "y"})
        summary = {
            "source": "demo",
            "path": str(demo_path),
            "n_rows": len(df),
            "start": df["ds"].min(),
            "end": df["ds"].max(),
        }
        return pd.DataFrame([summary])

    return None


def _load_model_comparison() -> Optional[pd.DataFrame]:
    metrics_path = Path("artifacts") / "reports" / "model_comparison.csv"
    if metrics_path.exists():
        return pd.read_csv(metrics_path)

    demo_path = DEMO_ARTIFACTS_DIR / "model_comparison.csv"
    if demo_path.exists():
        return pd.read_csv(demo_path)

    return None


def render_overview() -> None:
    try:
        st.header("Overview")

        st.markdown(
            """
            This page summarizes the current state of the DemandCast pipeline:
            data, models, backtests, and inventory optimization readiness.
            """
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Data status")
            series_summary = _load_series_summary()
            if series_summary is None:
                st.warning(
                    "No processed series found under `data/processed/`.\n\n"
                    "Run the data preparation script:\n\n"
                    "```bash\npython scripts/run_step1_prepare_data.py\n```"
                )
            else:
                st.success("Processed series detected.")
                st.dataframe(series_summary)

        with col2:
            st.subheader("Model leaderboard")
            comparison_df = _load_model_comparison()
            if comparison_df is None or comparison_df.empty:
                st.info(
                    "No model comparison report found yet.\n\n"
                    "To generate backtest reports, run:\n\n"
                    "```bash\n"
                    "python scripts/run_step2_backtest_models.py\n"
                    "python scripts/run_step3_train_lgbm.py\n"
                    "python scripts/run_step3_train_ensemble.py\n"
                    "python scripts/run_step3_backtest_lgbm_ensemble.py\n"
                    "```"
                )
            else:
                st.dataframe(comparison_df)

                if "wape" in comparison_df.columns:
                    best_idx = comparison_df["wape"].idxmin()
                    best_row = comparison_df.loc[best_idx]
                    st.metric(
                        "Best model (by WAPE)",
                        f"{best_row['model']}",
                        f"{best_row['wape']:.2f}%",
                    )

        st.markdown("---")
        st.markdown(
            """
            **Next steps**

            - Use the **Forecast** page to inspect model forecasts and download predictions.
            - Use the **Inventory** page to explore EOQ/ROP and scenario analysis.
            - Use the **Backtests** page to inspect fold-by-fold metrics and intervals.
            """
        )

    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error while rendering Overview page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the Overview page. "
            "Check the logs for details."
        )