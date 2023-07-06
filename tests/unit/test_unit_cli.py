""" Unit tests for the cli module. """
# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
import argparse
import os
import pathlib
import tempfile

import h5py
import numpy as np
import pytest
import pytest_mock

from grag_brainspace import cli, exceptions

IS_WINDOWS = os.name == "nt"


@pytest.fixture
def mock_args() -> argparse.Namespace:
    """Returns a mock argparse.Namespace object with default values for testing."""
    return argparse.Namespace(
        input_file=None,
        input_list=None,
        output="output.nii",
        force=False,
        parcellation=None,
    )


@pytest.fixture
def mock_files_volume() -> list[str]:
    """Returns a list of mock volume file paths."""
    return ["volume1.nii", "volume2.nii.gz"]


def test_raise_invalid_input_no_input(mock_args: argparse.Namespace) -> None:
    """Test that the _raise_invalid_input function raises an InputError when no
    input is provided."""
    with pytest.raises(exceptions.InputError) as exc_info:
        cli._raise_invalid_input(mock_args, [])

    assert "You must provide either an input file or a non-empty input list." in str(
        exc_info.value
    )


def test_raise_invalid_input_both_input(mock_args: argparse.Namespace) -> None:
    """Test that the _raise_invalid_input function raises an InputError when
    both an input file and an input list are provided."""
    mock_args.input_file = ["input.nii"]
    mock_args.input_list = "input.txt"

    with pytest.raises(exceptions.InputError) as exc_info:
        cli._raise_invalid_input(mock_args, mock_files_volume)  # type: ignore[arg-type]

    assert "You must provide either an input file or a non-empty input list." in str(
        exc_info.value
    )


def test_raise_invalid_input_output_exists(
    mock_args: argparse.Namespace,
    mock_files_volume: list[str],
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Test that the _raise_invalid_input function raises an InputError when the
    output file already exists."""

    mock_args.input_file = ["input.nii"]
    mocker.patch("pathlib.Path.exists", return_value=True)

    with pytest.raises(exceptions.InputError) as exc_info:
        cli._raise_invalid_input(mock_args, mock_files_volume)

    assert (
        "Output file already exists. Please choose a different output file or include the -f flag."
        in str(exc_info.value)
    )


def test_raise_invalid_input_output_exists_force(
    mock_args: argparse.Namespace,
    mock_files_volume: list[str],
) -> None:
    """Test that the _raise_invalid_input function raises no InputError when the
    output file already exists and the force flag is provided."""

    mock_args.input_file = ["input.nii"]
    mock_args.parcellation = "parcellation.nii"
    mock_args.force = True

    cli._raise_invalid_input(mock_args, mock_files_volume)

    # No exception raised


def test_raise_invalid_input_mixed_file_types(
    mock_args: argparse.Namespace, mock_files_volume: list[str]
) -> None:
    """Test that the _raise_invalid_input function raises an InputError when both
    GIFTI and NIFTI files are provided as input files."""

    mock_args.input_file = "input.nii"
    mock_args.parcellation = "parcellation.nii"
    mock_files_surface = ["surface1.gii", "surface2.gii"]

    with pytest.raises(exceptions.InputError) as exc_info:
        cli._raise_invalid_input(mock_args, mock_files_volume + mock_files_surface)

    assert "Input file(s) must be either be GIFTI or NIFTI files, not both." in str(
        exc_info.value
    )


def test_parse_input_list(mocker: pytest_mock.MockFixture) -> None:
    """Test that the _parse_input_list function correctly parses a list of
    files.
    """
    expected = ["file1", "file2", "file3"]
    mocker.patch("builtins.open", mocker.mock_open(read_data="\n".join(expected)))
    mocker.patch("pathlib.Path.exists", return_value=True)

    actual = cli._parse_input_list("")

    assert actual == expected


def parse_input_list_empty(mocker: pytest_mock.MockFixture) -> None:
    """Test that the _parse_input_list function raises an InputError when
    given an empty file.
    """
    mocker.patch("builtins.open", mocker.mock_open(read_data=""))

    with pytest.raises(exceptions.InputError) as exc_info:
        cli._parse_input_list("")

    assert "Input list is empty." in str(exc_info.value)


def test_parse_input_list_nonexistent_file(mocker: pytest_mock.MockFixture) -> None:
    """Test that the _parse_input_list function raises an InputError when
    given a nonexistent file.
    """
    input_list = ["file1", "file2", "file3"]
    mocker.patch("builtins.open", mocker.mock_open(read_data="\n".join(input_list)))

    with pytest.raises(exceptions.InputError) as exc_info:
        cli._parse_input_list("")

    assert "Not all files in input list exist." in str(exc_info.value)


def test_parse_input_list_duplicate(mocker: pytest_mock.MockFixture) -> None:
    """Test that the _parse_input_list function raises an InputError when
    given a list with duplicate files.
    """
    input_list = ["file1", "file2", "file2"]
    mocker.patch("builtins.open", mocker.mock_open(read_data="\n".join(input_list)))
    mocker.patch("pathlib.Path.exists", return_value=True)

    with pytest.raises(exceptions.InputError) as exc_info:
        cli._parse_input_list("")

    assert "Input list contains duplicate files." in str(exc_info.value)


@pytest.mark.skipif(
    IS_WINDOWS,
    reason="Windows does not support writing to and reading from the same temporary file.",
)
def test_save_numpy_array_h5():
    """Test that the _save_numpy_array function saves a numpy array to an h5 file
    with the correct name and content.
    """
    expected = np.array([[1, 2, 3], [4, 5, 6]])

    with tempfile.NamedTemporaryFile(suffix=".h5") as f:
        cli._save_numpy_array(expected, f.name)
        with h5py.File(f.name, "r") as h5:
            actual = np.array(h5["gradient_map"])

    assert np.allclose(actual, expected)


@pytest.mark.skipif(
    IS_WINDOWS,
    reason="Windows does not support writing to and reading from the same temporary file.",
)
def test_save_numpy_array_tsv():
    """Test that the _save_numpy_array function saves a numpy array to a tsv
    file with the correct content.
    """
    expected = np.array([[1, 2, 3], [4, 5, 6]])

    with tempfile.NamedTemporaryFile(suffix=".tsv") as f:
        cli._save_numpy_array(expected, f.name)
        actual = np.loadtxt(f.name, delimiter="\t")

    assert np.allclose(actual, expected)


@pytest.mark.skipif(
    IS_WINDOWS,
    reason="Windows does not support writing to and reading from the same temporary file.",
)
def test_save_numpy_array_csv():
    """Test that the _save_numpy_array function saves a numpy array to a csv
    file with the correct content.
    """
    expected = np.array([[1, 2, 3], [4, 5, 6]])

    with tempfile.NamedTemporaryFile(suffix=".csv") as f:
        cli._save_numpy_array(expected, f.name)
        actual = np.loadtxt(f.name, delimiter=",")

    assert np.allclose(actual, expected)


@pytest.mark.skipif(
    IS_WINDOWS,
    reason="Windows does not support writing to and reading from the same temporary file.",
)
def test_save_numpy_array_unknown_filetype(mocker):
    """Test that the _save_numpy_array function warns the user when an unknown
    filetype is given and saves as csv.
    """
    spy_warning_logger = mocker.spy(cli.logger, "warning")
    expected = np.array([[1, 2, 3], [4, 5, 6]])

    with tempfile.NamedTemporaryFile(suffix=".unknown") as f:
        cli._save_numpy_array(expected, f.name)
        actual = np.loadtxt(f.name, delimiter=",")

    assert np.allclose(actual, expected)
    assert spy_warning_logger.call_count == 1
