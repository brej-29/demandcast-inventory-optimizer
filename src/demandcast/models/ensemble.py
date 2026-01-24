from typing import Any

from ..logging_utils import get_logger

logger = get_logger(__name__)


class EnsembleModel:
    """
    Placeholder for an ensemble of forecasting models.

    The concrete implementation will combine individual model forecasts and
    will be added in a later step.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logger.info(
            "Initializing EnsembleModel placeholder with args=%s, kwargs=%s",
            args,
            kwargs,
        )

    def fit(self, *args: Any, **kwargs: Any) -> "EnsembleModel":
        logger.info("Called fit on EnsembleModel placeholder")
        raise NotImplementedError(
            "EnsembleModel.fit will be implemented in a later step."
        )

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        logger.info("Called predict on EnsembleModel placeholder")
        raise NotImplementedError(
            "EnsembleModel.predict will be implemented in a later step."
        )