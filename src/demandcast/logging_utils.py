import logging


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_LEVEL = logging.INFO


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger with a standard format and INFO as the default level.

    This helper is safe to import from anywhere in the project. It configures
    a basic console handler the first time it is used for a given logger name
    and then reuses that configuration on subsequent calls.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Logger already configured
        return logger

    logger.setLevel(DEFAULT_LEVEL)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(handler)
    logger.propagate = False

    return logger