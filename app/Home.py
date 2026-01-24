import logging
import textwrap

import streamlit as st

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Render the DemandCast home page."""
    try:
        logger.info("Rendering Home page")

        st.set_page_config(
            page_title="DemandCast - Store Item Demand Forecasting",
            page_icon=":bar_chart:",
            layout="wide",
        )

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
            "streamlit run app/Home.py",
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

            - Project skeleton and app navigation
            - Environment + data download scaffolding
            - Forecasting models and inventory optimization (upcoming steps)
            """
        )

        st.info(
            "This is a minimal, fast-loading page that does not require any data to be "
            "present. It is safe to run immediately after cloning the repository."
        )

    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error while rendering Home page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the home page. "
            "Check the application logs for details."
        )


if __name__ == "__main__":
    main()