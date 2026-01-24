import logging

import streamlit as st

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Render the backtesting and evaluation page placeholder."""
    try:
        logger.info("Rendering Backtests page")

        st.title("Backtests")
        st.write(
            "This page will provide backtesting tools to evaluate forecasting models "
            "and resulting inventory policies over historical data."
        )

        st.markdown(
            """
            Planned functionality:

            - Configure rolling- and expanding-window backtests
            - Compare models on RMSE, MAPE, sMAPE and inventory-related KPIs
            - Visualize forecast errors over time and by segment
            - Save evaluation reports to the `artifacts/reports/` directory
            """
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error in Backtests page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the Backtests page. "
            "Check logs for details."
        )


if __name__ == "__main__":
    main()