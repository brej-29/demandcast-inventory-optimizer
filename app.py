import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from demandcast.ui import render_home  # noqa: E402
from demandcast.logging_utils import get_logger  # noqa: E402

logger = get_logger(__name__)


def main() -> None:
    try:
        st.set_page_config(
            page_title="DemandCast - Store Item Demand Forecasting",
            page_icon=":bar_chart:",
            layout="wide",
        )
    except Exception:
        # set_page_config can only be called once per app; ignore if already set.
        pass

    render_home()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error in root app.py: %s", exc)
        raise