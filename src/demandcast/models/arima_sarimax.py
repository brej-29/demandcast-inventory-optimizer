from typing import Any

from ..logging_utils import get_logger

logger = get_logger(__name__)


class ARIMASARIMAXModel:
    """
    Placeholder for an ARIMA/SARIMAX-based forecasting model.

    The concrete implementation (hyperparameters, fitting, prediction, etc.)
    will be provided in a later step.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logger.info(
            "Initializing ARIMASARIMAXModel placeholder with args=%s, kwargs=%s",
            args,
            kwargs,
        )

    def fit(self, *args: Any, **kwargs: Any) -> "ARIMASARIMAXModel":
        logger.info("Called fit on ARIMASARIMAXModel placeholder")
        raise NotImplementedError(
            "ARIMASARIMAXModel.fit will be implemented in a later step."
        )

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        logger.info("Called predict on ARIMASARIMAXModel placeholder")
        raise NotImplementedError(
            "ARIMASARIMAXModel.predict will be implemented in a later step."
        )