from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..config import FORECAST_HORIZON_DAYS, artifact_config
from ..data.preprocess import load_processed_series
from ..logging_utils import get_logger
from ..models import (
    ARIMASARIMAXModel,
    ETSModel,
    LGBMForecaster,
    ProphetFallbackModel,
    EnsembleForecaster,
)
from ..paths import DEMO_DATA_DIR
from ..paths import ensure_directories

logger = get_logger(__name__)


MODEL_LABELS = {
    "ensemble": "Ensemble (recommended)",
    "lgbm": "LightGBM",
    "sarimax": "SARIMAX",
    "ets": "ETS",
    "prophet_or_fallback": "Prophet or SARIMAX fallback",
}


def _load_series_for_forecast() -> Optional[pd.DataFrame]:
    try:
        series_df, _ = load_processed_series()
        return series_df
    except FileNotFoundError:
        demo_series_path = DEMO_DATA_DIR / "demo_series.csv"
        if demo_series_path.exists():
            df = pd.read_csv(demo_series_path)
            df["ds"] = pd.to_datetime(df["ds"])
            if "y" not in df.columns and "sales" in df.columns:
                df = df.rename(columns={"sales": "y"})
            return df
        return None


def _load_trained_model(name: str):
    models_dir = artifact_config.models_dir
    path = models_dir / f"{name}.pkl"
    if not path.exists():
        logger.warning("Model artifact %s not found.", path)
        return None
    if name == "lgbm":
        return LGBMForecaster.load(path)
    if name == "ensemble":
        return EnsembleForecaster.load(path)
    if name == "sarimax":
        import pickle

        with path.open("rb") as f:
            return pickle.load(f)
    if name == "ets":
        import pickle

        with path.open("rb") as f:
            return pickle.load(f)
    if name == "prophet_or_fallback":
        import pickle

        with path.open("rb") as f:
            return pickle.load(f)
    return None


def _build_forecast_from_model(
    model_name: str,
    horizon: int,
    series_df: pd.DataFrame,
) -> Optional[pd.DataFrame]:
    model = _load_trained_model(model_name)
    if model is None:
        return None

    last_ds = pd.to_datetime(series_df["ds"]).max()
    future_dates = pd.date_range(start=last_ds + pd.Timedelta(days=1), periods=horizon, freq="D")
    future_df = pd.DataFrame({"ds": future_dates})

    preds = model.predict(future_df, horizon=horizon)
    return preds


def _build_plot(series_df: pd.DataFrame, forecast_df: pd.DataFrame, model_name: str) -> go.Figure:
    df = series_df.copy()
    df["ds"] = pd.to_datetime(df["ds"])
    forecast_df = forecast_df.copy()
    forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["ds"],
            y=df["y"],
            mode="lines",
            name="Historical demand",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_df["ds"],
            y=forecast_df["yhat"],
            mode="lines",
            name=f"Forecast ({MODEL_LABELS.get(model_name, model_name)})",
        )
    )

    if "yhat_lower" in forecast_df.columns and "yhat_upper" in forecast_df.columns:
        fig.add_trace(
            go.Scatter(
                x=pd.concat([forecast_df["ds"], forecast_df["ds"][::-1]]),
                y=pd.concat([forecast_df["yhat_upper"], forecast_df["yhat_lower"][::-1]]),
                fill="toself",
                fillcolor="rgba(0, 123, 255, 0.2)",
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                showlegend=True,
                name="Prediction interval",
            )
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Demand",
        hovermode="x unified",
    )
    return fig


def render_forecast() -> None:
    try:
        st.header("Forecast")

        series_df = _load_series_for_forecast()
        if series_df is None:
            st.warning(
                "No processed series is available and no demo assets were found.\n\n"
                "Run the data and training pipeline first:\n\n"
                "```bash\n"
                "python scripts/run_step1_prepare_data.py\n"
                "python scripts/run_step2_train_models.py\n"
                "python scripts/run_step3_train_lgbm.py\n"
                "python scripts/run_step3_train_ensemble.py\n"
                "```"
            )
            return

        model_key = st.selectbox(
            "Select model",
            options=list(MODEL_LABELS.keys()),
            format_func=lambda k: MODEL_LABELS.get(k, k),
            index=0,
        )

        horizon = st.slider(
            "Forecast horizon (days)",
            min_value=7,
            max_value=FORECAST_HORIZON_DAYS,
            value=FORECAST_HORIZON_DAYS,
            step=7,
        )

        if st.button("Generate forecast"):
            preds = _build_forecast_from_model(model_key, horizon, series_df)
            if preds is None or preds.empty:
                st.error(
                    "Selected model is not trained yet or produced no predictions.\n\n"
                    "Make sure you have run the relevant training scripts."
                )
                return

            fig = _build_plot(series_df, preds, model_key)
            st.plotly_chart(fig, use_container_width=True)

            csv = preds.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download forecast CSV",
                data=csv,
                file_name=f"forecast_{model_key}.csv",
                mime="text/csv",
            )
        else:
            st.info("Click **Generate forecast** to compute and display model predictions.")

    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error while rendering Forecast page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the Forecast page. "
            "Check the logs for details."
        )