""" CLI Integration tests. """
# pylint: disable=redefined-outer-name
import argparse
import tempfile

import h5py
import nibabel as nib
import numpy as np
import pytest
import pytest_mock
from nibabel import gifti

from grag_brainspace import cli


class MockParser:
    """A mock parser class used for testing command line interface (CLI) functionality.

    This class is used to simulate the behavior of the `argparse.ArgumentParser` class
    in order to test the CLI functionality of the `grag_brainspace` package.
    """

    def __init__(
        self, input_files: list[str], output_file: str, parcellation: str = None
    ) -> None:
        self.input_file = input_files
        self.output_file = output_file
        self.parcellation = parcellation

    def parse_args(self) -> argparse.Namespace:
        """Parses the mocked command line arguments and returns a Namespace object.

        Returns:
            A Namespace object containing the parsed command line arguments.
        """
        return argparse.Namespace(
            input_file=self.input_file,
            input_list=None,
            output=self.output_file,
            n_components=2,
            force=True,
            parcellation=self.parcellation,
            sparsity=0.0,  # Low sparsity to ensure enough data remains with small test data
            kernel="cosine",
            dimensionality_reduction="dm",
        )


@pytest.fixture
def nifti_data_file() -> str:
    """Return a mock NIfTI temporary data file."""
    data = np.random.rand(10, 10, 10, 10)
    with tempfile.NamedTemporaryFile(suffix=".nii") as file:
        nib.save(nib.Nifti1Image(data, np.eye(4)), file.name)
        yield file.name


@pytest.fixture
def nifti_parcellation_file() -> str:
    """Return a mock NIfTI temporary parcellation file."""
    parcellation = np.ones((10, 10, 10), dtype=np.int32)
    parcellation[5:, :, :] = 2
    parcellation[:5, 5:, :] = 3
    with tempfile.NamedTemporaryFile(suffix=".nii") as file:
        nib.save(nib.Nifti1Image(parcellation, np.eye(4)), file.name)
        yield file.name


@pytest.fixture
def surface_data_file() -> str:
    """Return a mock surface data file."""
    data = np.random.rand(10, 20).astype(np.float32)
    with tempfile.NamedTemporaryFile(suffix=".func.gii") as file:
        gii = gifti.GiftiImage(darrays=[gifti.GiftiDataArray(data)])
        nib.save(gii, file.name)
        yield file.name


@pytest.fixture
def surface_parcellation_file() -> str:
    """Return a mock surface parcellation file."""
    parcellation = np.ones((10,), dtype=np.int32)
    parcellation[4:8] = 2
    parcellation[8:] = 3
    with tempfile.NamedTemporaryFile(suffix=".shape.gii") as file:
        gii = gifti.GiftiImage(darrays=[gifti.GiftiDataArray(parcellation)])
        nib.save(gii, file.name)
        yield file.name


def test_volume_input(
    mocker: pytest_mock.MockerFixture,
    nifti_data_file: str,
    nifti_parcellation_file: str,
) -> None:
    """Test that the CLI works with a volume input."""
    with tempfile.NamedTemporaryFile(suffix=".h5") as output:
        mocker.patch(
            "grag_brainspace.cli._get_parser",
            return_value=MockParser(
                input_files=[nifti_data_file],
                output_file=output.name,
                parcellation=nifti_parcellation_file,
            ),
        )

        cli.main()
        output = np.array(h5py.File(output.name, "r")["gradient_map"])

    assert output.shape == (3, 2)  # three parcels, two components


def test_surface_input(
    mocker: pytest_mock.MockerFixture,
    surface_data_file: str,
    surface_parcellation_file: str,
) -> None:
    """Test that the CLI works with a surface input."""
    with tempfile.NamedTemporaryFile(suffix=".h5") as output:
        mocker.patch(
            "grag_brainspace.cli._get_parser",
            return_value=MockParser(
                input_files=[surface_data_file],
                output_file=output.name,
                parcellation=surface_parcellation_file,
            ),
        )

        cli.main()
        output = np.array(h5py.File(output.name, "r")["gradient_map"])

    assert output.shape == (3, 2)  # three parcels, two components
