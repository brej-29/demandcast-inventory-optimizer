import textwrap

import streamlit as st

from ..logging_utils import get_logger

logger = get_logger(__name__)


def render_home() -> None:
    try:
        logger.info("Rendering Home page via ui.home.render_home")

        st.title("Hello DemandCast")
        st.subheader("Time Series Forecasting & Inventory Optimization Dashboard")

        st.markdown(
            textwrap.dedent(
                """
                This is the **starting point** for the DemandCast application.

                The goal of this project is to explore demand forecasting and inventory
                optimization for the Kaggle competition
                *"Store Item Demand Forecasting Challenge"* (`demand-forecasting-kernels-only`).
                """
            )
        )

        st.markdown("### Quickstart (local development)")
        st.code(
            "python -m venv .venv\n"
            "source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate\n"
            "pip install --upgrade pip\n"
            "pip install -r requirements.txt\n"
            "streamlit run app.py",
            language="bash",
        )

        st.markdown(
            """
            ### Dataset

            The app is designed to work with the Kaggle competition data:
            `demand-forecasting-kernels-only`.

            Use the helper scripts in `scripts/` to download the data into `data/raw/`
            once your Kaggle API token is configured.
            """
        )

        st.markdown(
            """
            ### Status

            - Data ingestion and preprocessing pipeline
            - Baseline models and backtesting
            - LightGBM and ensemble forecasting
            - Inventory optimization scenarios
            """
        )

        st.info(
            "This home page is fast to load and does not require any data to be present. "
            "It is safe to run immediately after cloning the repository."
        )

    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error while rendering Home page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the home page. "
            "Check the application logs for details."
        )