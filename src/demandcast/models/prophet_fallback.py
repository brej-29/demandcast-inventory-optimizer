from typing import Any

from ..logging_utils import get_logger

logger = get_logger(__name__)


class ProphetFallbackModel:
    """
    Placeholder for a Prophet-based forecasting model.

    This is intended as a fallback / alternative to classical models.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logger.info(
            "Initializing ProphetFallbackModel placeholder with args=%s, kwargs=%s",
            args,
            kwargs,
        )

    def fit(self, *args: Any, **kwargs: Any) -> "ProphetFallbackModel":
        logger.info("Called fit on ProphetFallbackModel placeholder")
        raise NotImplementedError(
            "ProphetFallbackModel.fit will be implemented in a later step."
        )

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        logger.info("Called predict on ProphetFallbackModel placeholder")
        raise NotImplementedError(
            "ProphetFallbackModel.predict will be implemented in a later step."
        )