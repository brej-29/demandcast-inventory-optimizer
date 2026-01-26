import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from demandcast.ui.forecast import render_forecast  # noqa: E402
from demandcast.logging_utils import get_logger  # noqa: E402

logger = get_logger(__name__)


def main() -> None:
    render_forecast()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error in Forecast page: %s", exc)
        raise