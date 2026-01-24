from pathlib import Path
from typing import Optional

import pandas as pd

from ..logging_utils import get_logger
from ..paths import RAW_DATA_DIR

logger = get_logger(__name__)


def load_competition_train(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load the Kaggle competition training data from CSV.

    Parameters
    ----------
    path:
        Optional explicit path to the CSV file. If not provided, defaults to
        RAW_DATA_DIR / "train.csv".

    Returns
    -------
    pd.DataFrame
        Loaded training data.

    Raises
    ------
    FileNotFoundError
        If the expected CSV file does not exist.
    """
    csv_path = Path(path) if path is not None else RAW_DATA_DIR / "train.csv"

    if not csv_path.exists():
        logger.warning("Training data not found at %s", csv_path)
        raise FileNotFoundError(
            f"Expected training data at {csv_path}. "
            "Run the Kaggle download script in scripts/ to fetch the dataset."
        )

    logger.info("Loading training data from %s", csv_path)
    return pd.read_csv(csv_path)