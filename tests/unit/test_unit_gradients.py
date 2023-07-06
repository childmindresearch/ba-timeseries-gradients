""" Unit tests for the gradients module. """
# pylint: disable=protected-access
import numpy as np
import pytest
import pytest_mock

from grag_brainspace import exceptions, gradients


def test_compute_gradients(mocker: pytest_mock.MockFixture) -> None:
    """Test that the compute_gradients function calls the correct functions."""
    mocker.patch(
        "grag_brainspace.gradients._get_connectivity_matrix",
        return_value=np.ones((3, 3)),
    )

    actual = gradients.compute_gradients(files=[], sparsity=0)

    assert np.allclose(actual, 0)


def test_compute_gradients_brainspace_error(mocker: pytest_mock.MockFixture) -> None:
    """Test that the compute_gradients function raises an error when
    BrainSpace raises an error."""
    mocker.patch(
        "grag_brainspace.gradients._get_connectivity_matrix",
        return_value=np.ones((3, 3)),
    )
    mocker.patch(
        "brainspace.gradient.GradientMaps",
        side_effect=Exception("Error"),
    )

    with pytest.raises(exceptions.BrainSpaceError):
        gradients.compute_gradients(files=[])


def test_connevtivity_matrix_from_2d_success(mocker: pytest_mock.MockerFixture) -> None:
    """Test that the connectivity matrix is computed correctly from a 2D
    timeseries."""
    mocker.patch("nibabel.load")
    mocker.patch(
        "grag_brainspace.gradients._get_nifti_gifti_data", return_value=np.eye(3)
    )
    expected = np.eye(3)
    expected[~np.eye(3, dtype=bool)] = -0.5

    actual = gradients._get_connectivity_matrix(["file1", "file2"])

    assert np.allclose(actual, expected)


def test_connevtivity_matrix_from_4d_success(mocker: pytest_mock.MockerFixture) -> None:
    """Test that the connectivity matrix is computed correctly from a 4D
    timeseries."""
    data_4d = np.concatenate((np.ones((2, 2, 2, 2)), np.zeros((2, 2, 2, 1))), axis=3)
    mocker.patch("nibabel.load")
    mocker.patch(
        "grag_brainspace.gradients._get_nifti_gifti_data", return_value=data_4d
    )
    expected = np.ones((8, 8))

    actual = gradients._get_connectivity_matrix(["file1", "file2"])

    assert np.allclose(actual, expected)


def test_parcellate_2d_timeseries_success() -> None:
    """Test that the 2D timeseries are parcellated correctly."""
    timeseries = [[1, 2, 1], [1, 1, 1], [2, 2, 2]]
    parcellation = [1, 1, 2]
    expected = [[1.5, 1], [1, 1], [2, 2]]

    actual = gradients._parcellate_timeseries(
        timeseries=timeseries,
        parcellation=parcellation,
    )

    assert np.allclose(actual, expected)


def test_parcellate_timeseries_faulty_dimensions() -> None:
    """Test that an error is raised when the parcellation dimensions do not
    match the timeseries dimensions."""
    with pytest.raises(exceptions.InputError):
        gradients._parcellate_timeseries(
            timeseries=[[1, 2, 3], [4, 5, 6]],
            parcellation=[[1, 2], [3, 4]],
        )
