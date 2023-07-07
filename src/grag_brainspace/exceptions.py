""" Custom exceptions for the grag_brainspace package. """
import logging

from grag_brainspace import logs

LOGGER_NAME = logs.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class BaseLoggingError(Exception):
    """Base exception for logging errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        logger.error(self.message)


class InputError(BaseLoggingError):
    """Exception raised when an input value is invalid or incorrect."""


class InternalError(BaseLoggingError):
    """Exception raised when an internal error occurs. These should never happen."""


class BrainSpaceError(BaseLoggingError):
    """Exception raised when a BrainSpace error occurs."""
