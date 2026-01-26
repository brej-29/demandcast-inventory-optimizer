from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

import pandas as pd

from ..config import ARTIFACTS_DIR
from ..logging_utils import get_logger

logger = get_logger(__name__)

REPORTS_DIR = ARTIFACTS_DIR / "reports"


def _ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def save_predictions_csv(df: pd.DataFrame, name: str) -> Path:
    _ensure_reports_dir()
    path = REPORTS_DIR / f"predictions_{name}.csv"
    df.to_csv(path, index=False)
    logger.info("Saved predictions for %s to %s", name, path)
    return path


def save_summary_table(summary_rows: Iterable[Mapping[str, Any]], filename: str) -> Path:
    _ensure_reports_dir()
    path = REPORTS_DIR / filename
    df = pd.DataFrame(list(summary_rows))
    df.to_csv(path, index=False)
    logger.info("Saved summary table to %s", path)
    return path


def save_json_report(payload: Mapping[str, Any], filename: str) -> Path:
    _ensure_reports_dir()
    path = REPORTS_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    logger.info("Saved JSON report to %s", path)
    return path