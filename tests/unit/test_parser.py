"""Tests for the parser module."""
# pylint: disable=protected-access
import argparse
import pathlib
import tempfile

import pytest

from ba_timeseries_gradients import parser


def test_get_parser() -> None:
    """Test the get_parser function to ensure it returns an instance of argparse.ArgumentParser."""
    parser_object = parser.get_parser()
    assert isinstance(parser_object, argparse.ArgumentParser)


def test_path_exists_success() -> None:
    """Test the path_exists function for a successful case."""
    with tempfile.TemporaryDirectory() as temp_dir:
        assert parser._path_exists(temp_dir) == pathlib.Path(temp_dir)


def test_path_exists_failure() -> None:
    """Test the path_exists function for a failure case."""
    with pytest.raises(argparse.ArgumentTypeError):
        parser._path_exists("not_a_path")


def test_is_positive_integer_success() -> None:
    """Test the _is_positive_integer function for a successful case."""
    assert parser._is_positive_integer("1") == 1


def test_is_positive_integer_failure_not_int() -> None:
    """Test the _is_positive_integer function for a float."""
    with pytest.raises(argparse.ArgumentTypeError):
        parser._is_positive_integer("0.5")


def test_is_positive_integer_failure_negative() -> None:
    """Test the _is_positive_integer function for a negative integer."""
    with pytest.raises(argparse.ArgumentTypeError):
        parser._is_positive_integer("-1")


def test_is_positive_integer_failure_zero() -> None:
    """Test the _is_positive_integer function for zero."""
    with pytest.raises(argparse.ArgumentTypeError):
        parser._is_positive_integer("0")


def test_is_between_zero_and_one_success() -> None:
    """Test the _is_between_zero_and_one function for a successful case."""
    assert parser._is_between_zero_and_one("0") == 0


def test_is_between_zero_and_one_failure_is_one() -> None:
    """Test the _is_between_zero_and_one function for a failure case."""
    with pytest.raises(argparse.ArgumentTypeError):
        parser._is_between_zero_and_one("1")


def test_is_between_zero_and_one_failure_is_negative() -> None:
    """Test the _is_between_zero_and_one function for a failure case."""
    with pytest.raises(argparse.ArgumentTypeError):
        parser._is_between_zero_and_one("-1")
