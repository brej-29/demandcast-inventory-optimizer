from typing import Any

from ..logging_utils import get_logger

logger = get_logger(__name__)


class LightGBMModel:
    """
    Placeholder for a gradient boosting (LightGBM) forecasting model.

    The concrete implementation (feature matrix construction, training,
    prediction, and hyperparameter search) will be added in a later step.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logger.info(
            "Initializing LightGBMModel placeholder with args=%s, kwargs=%s",
            args,
            kwargs,
        )

    def fit(self, *args: Any, **kwargs: Any) -> "LightGBMModel":
        logger.info("Called fit on LightGBMModel placeholder")
        raise NotImplementedError(
            "LightGBMModel.fit will be implemented in a later step."
        )

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        logger.info("Called predict on LightGBMModel placeholder")
        raise NotImplementedError(
            "LightGBMModel.predict will be implemented in a later step."
        )