"""Structured logging configuration for STORMNET."""

import logging
import sys
from apps.api.core.config import settings


def setup_logging() -> logging.Logger:
    """Configures structured console logging for the application."""
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logger = logging.getLogger("stormnet")
    return logger


logger = setup_logging()
