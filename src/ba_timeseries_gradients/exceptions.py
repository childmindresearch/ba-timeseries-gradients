""" Custom exceptions for the ba_timeseries_gradients package. """
import logging

from ba_timeseries_gradients import logs

LOGGER_NAME = logs.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class BaseLoggingError(Exception):
    """Base exception for logging errors."""

    def __init__(self, message: str):
        self.message = message
        logger.error(self.message)
        super().__init__(self.message)


class InputError(BaseLoggingError):
    """Exception raised when an input value is invalid or incorrect."""


class InternalError(BaseLoggingError):
    """Exception raised when an internal error occurs. These should never happen."""
