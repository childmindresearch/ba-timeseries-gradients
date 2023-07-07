""" Unit tests for the utils module. """
import dataclasses
import json
import os
import pathlib
import tempfile

import h5py
import numpy as np
import pytest

from grag_brainspace import exceptions, utils

IS_WINDOWS = os.name == "nt"


@dataclasses.dataclass
class MockArgparse:
    """A mock argparse class used for testing purposes."""

    output_dir: pathlib.Path
    output_format: str


@pytest.mark.skipif(
    IS_WINDOWS,
    reason="Windows does not support writing to and reading from the same temporary file.",
)
def test_save_hdf5() -> None:
    """Test that the _save_numpy_array function saves a numpy array to an h5 file
    with the correct name and content.
    """
    expected_1 = np.array([[1, 2, 3], [4, 5, 6]])
    expected_2 = np.array([1, 2, 3])

    with tempfile.NamedTemporaryFile(suffix=".h5") as f:
        utils.save_hdf5(expected_1, expected_2, f.name)
        with h5py.File(f.name, "r") as h5:
            actual_1 = np.array(h5["gradients"])
            actual_2 = np.array(h5["lambdas"])

    assert np.allclose(actual_1, expected_1)
    assert np.allclose(actual_2, expected_2)


@pytest.mark.skipif(
    IS_WINDOWS,
    reason="Windows does not support writing to and reading from the same temporary file.",
)
def test_save_json() -> None:
    """Test that the save_json function saves a dictionary to a json file
    with the correct name and content.
    """
    expected_1 = np.array([1, 2, 3])
    expected_2 = np.array([2, 3, 4])

    with tempfile.NamedTemporaryFile(suffix=".json") as tmp_fb:
        utils.save_json(expected_1, expected_2, tmp_fb.name)
        with open(tmp_fb.name, "r", encoding="utf-8") as json_fb:
            actual = json.load(json_fb)

    assert actual["gradients"] == expected_1.tolist()
    assert actual["lambdas"] == expected_2.tolist()


def test_save_internal_error() -> None:
    """Test that the save_json function raises an error if the file extension is not .json or .h5."""
    parser = MockArgparse(pathlib.Path("."), "txt")

    with pytest.raises(exceptions.InternalError):
        utils.save(np.array([1, 2, 3]), np.array([2, 3, 4]), parser)  # type: ignore[arg-type]
