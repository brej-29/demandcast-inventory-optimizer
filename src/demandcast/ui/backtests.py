from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from ..logging_utils import get_logger
from ..paths import DEMO_ARTIFACTS_DIR

logger = get_logger(__name__)


def _load_backtest_summary() -> Optional[pd.DataFrame]:
    metrics_path = Path("artifacts") / "reports" / "model_comparison.csv"
    if metrics_path.exists():
        return pd.read_csv(metrics_path)

    demo_path = DEMO_ARTIFACTS_DIR / "model_comparison.csv"
    if demo_path.exists():
        return pd.read_csv(demo_path)

    return None


def _load_predictions(model: str) -> Optional[pd.DataFrame]:
    path = Path("artifacts") / "reports" / f"predictions_{model}.csv"
    if path.exists():
        df = pd.read_csv(path)
        df["ds"] = pd.to_datetime(df["ds"])
        return df

    demo_path = DEMO_ARTIFACTS_DIR / f"predictions_{model}.csv"
    if demo_path.exists():
        df = pd.read_csv(demo_path)
        df["ds"] = pd.to_datetime(df["ds"])
        return df

    return None


def render_backtests() -> None:
    try:
        st.header("Backtests")

        summary_df = _load_backtest_summary()
        if summary_df is None or summary_df.empty:
            st.warning(
                "No backtest reports found.\n\n"
                "Run the following scripts to generate them:\n\n"
                "```bash\n"
                "python scripts/run_step2_backtest_models.py\n"
                "python scripts/run_step3_train_lgbm.py\n"
                "python scripts/run_step3_train_ensemble.py\n"
                "python scripts/run_step3_backtest_lgbm_ensemble.py\n"
                "```"
            )
            return

        st.subheader("Model comparison table")
        st.dataframe(summary_df)

        model_options = summary_df["model"].tolist()
        model = st.selectbox("Select model to inspect", options=model_options)

        preds_df = _load_predictions(model)
        if preds_df is None or preds_df.empty:
            st.warning(f"No prediction file found for model '{model}'.")
            return

        if "fold" in preds_df.columns:
            st.subheader("Fold-by-fold error distribution (absolute error)")
            preds_df["abs_error"] = (preds_df["y"] - preds_df["yhat"]).abs()
            fig = px.box(
                preds_df,
                x="fold",
                y="abs_error",
                points="all",
                title="Absolute error by fold",
            )
            st.plotly_chart(fig, use_container_width=True)

        if "yhat_lower" in preds_df.columns and "yhat_upper" in preds_df.columns:
            st.subheader("Prediction intervals coverage (by fold)")
            preds_df["covered"] = (preds_df["y"] >= preds_df["yhat_lower"]) & (
                preds_df["y"] <= preds_df["yhat_upper"]
            )
            coverage = preds_df.groupby("fold")["covered"].mean().reset_index()
            fig_cov = px.bar(
                coverage,
                x="fold",
                y="covered",
                title="Fraction of observations inside prediction interval by fold",
                labels={"covered": "Coverage"},
            )
            st.plotly_chart(fig_cov, use_container_width=True)

    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error while rendering Backtests page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the Backtests page. "
            "Check the logs for details."
        )