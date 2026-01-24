import logging

import streamlit as st

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Render the high-level project overview page."""
    try:
        logger.info("Rendering Overview page")

        st.title("Overview")
        st.write(
            "High-level overview of the DemandCast project. "
            "This page will summarize the problem, dataset, and key modeling ideas."
        )

        st.markdown(
            """
            **Planned sections:**

            - Problem statement and business context
            - Dataset summary and known limitations
            - High-level architecture overview
            - Links to EDA notebooks and generated reports
            """
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error in Overview page: %s", exc)
        st.error(
            "An unexpected error occurred while rendering the Overview page. "
            "Check logs for details."
        )


if __name__ == "__main__":
    main()