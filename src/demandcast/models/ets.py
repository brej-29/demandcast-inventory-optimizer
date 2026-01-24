from typing import Any

from ..logging_utils import get_logger

logger = get_logger(__name__)


class ETSModel:
    """
    Placeholder for an Exponential Smoothing (ETS) forecasting model.

    The concrete implementation will be provided in a later step.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logger.info(
            "Initializing ETSModel placeholder with args=%s, kwargs=%s",
            args,
            kwargs,
        )

    def fit(self, *args: Any, **kwargs: Any) -> "ETSModel":
        logger.info("Called fit on ETSModel placeholder")
        raise NotImplementedError("ETSModel.fit will be implemented in a later step.")

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        logger.info("Called predict on ETSModel placeholder")
        raise NotImplementedError(
            "ETSModel.predict will be implemented in a later step."
        )