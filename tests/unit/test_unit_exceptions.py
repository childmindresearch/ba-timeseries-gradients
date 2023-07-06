""" Unit tests for the grag_brainspace.exceptions module. """
import pytest
import pytest_mock

from grag_brainspace import exceptions


@pytest.mark.parametrize(
    "exception_type",
    [
        exceptions.BaseLoggingError,
        exceptions.InputError,
        exceptions.BrainSpaceError,
    ],
)
def test_logging_error(mocker: pytest_mock.MockFixture, exception_type: Exception):
    """
    Test that a BaseLoggingError is raised with the correct message and that the error is logged.
    """
    spy_error_logger = mocker.spy(exceptions.logger, "error")

    with pytest.raises(exception_type):
        raise exception_type("Test message")

    spy_error_logger.assert_called_once_with("Test message")
