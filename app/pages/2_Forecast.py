import logging

import streamlit as st

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Render the forecasting page placeholder."""
    try:
        logger.info("Rendering Forecast page")

        st.title("Forecast")
        st.write(
            "This page will host demand forecasting workflows, model configuration, "
            "and visualizations. For now, it is a placeholder."
        )

        st.markdown(
            """
            Planned functionality:

            - Select forecasting horizon and aggregation level
            - Trigger model training / updating
            - Visualize forecasts vs. actuals
            - Export forecasts for downstream inventory planning
            """
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error in Forecast page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the Forecast page. "
            "Check logs for details."
        )


if __name__ == "__main__":
    main()