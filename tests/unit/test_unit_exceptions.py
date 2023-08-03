""" Unit tests for the ba_timeseries_gradients.exceptions module. """
import pytest
import pytest_mock

from ba_timeseries_gradients import exceptions


@pytest.mark.parametrize(
    "exception_type",
    [
        exceptions.BaseLoggingError,
        exceptions.InputError,
        exceptions.InternalError,
    ],
)
def test_logging_error(
    mocker: pytest_mock.MockFixture,
    exception_type: exceptions.BaseLoggingError | exceptions.InputError,
):
    """
    Test that a BaseLoggingError is raised with the correct message and that the error is logged.
    """
    spy_error_logger = mocker.spy(exceptions.logger, "error")

    with pytest.raises(exception_type):  # type: ignore[call-overload]
        raise exception_type("Test message")  # type: ignore[operator]

    spy_error_logger.assert_called_once_with("Test message")
