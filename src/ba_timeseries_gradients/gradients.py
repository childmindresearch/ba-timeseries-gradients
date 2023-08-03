""" Module for computing gradients. """
import logging
import pathlib
from collections import abc

import nibabel as nib
import numpy as np
from brainspace import gradient
from brainspace.utils import parcellation as brainspace_parcellation
from nibabel import filebasedimages
from numpy import typing as npt

from ba_timeseries_gradients import exceptions, logs

LOGGER_NAME = logs.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def compute_gradients(
    files: abc.Collection[str | pathlib.Path],
    *,
    parcellation_file: str | pathlib.Path | None = None,
    approach: str = "dm",
    kernel: str = "cosine",
    n_components: int = 10,
    sparsity: float = 0.9,
) -> tuple[np.ndarray, np.ndarray]:
    """Computes the gradients for a collection of files.

    Args:
        files: A collection of file paths containing timeseries data.
        parcellation_file: A file path containing parcellation data. If None,
            the timeseries data is not parcellated.
        approach: The dimensionality reduction approach to use.
        kernel: The kernel to use for the gradient computation.
        n_components: The number of gradient components to compute.
        sparsity: The sparsity level to use for the gradient computation.

    Returns:
        numpy.ndarray: The computed gradients.
        numpy.ndarray: The computed lambdas.

    Notes:
        The gradient computation is performed using the BrainSpace package.
        For up-to-date information on the available approaches, kernels, and
        parameters, please refer to the BrainSpace documentation:
        https://brainspace.readthedocs.io/.
    """
    logger.info("Computing connectivity matrix...")
    connectivity_matrix = _get_connectivity_matrix(files, parcellation_file)

    logger.info("Computing gradients...")
    gradient_map = gradient.GradientMaps(
        n_components=n_components,
        kernel=kernel,
        approach=approach,
        alignment=None,
        random_state=0,
    )
    gradient_map.fit(connectivity_matrix, sparsity=sparsity)

    return gradient_map.gradients_, gradient_map.lambdas_


def _get_connectivity_matrix(
    files: abc.Collection[str | pathlib.Path],
    parcellation_file: str | pathlib.Path | None = None,
) -> np.ndarray:
    """
    Computes the connectivity matrix for a collection of files.

    Args:
        files: A collection of file paths containing timeseries data.
        parcellation_file: A file path containing parcellation data. If None,
            the timeseries data is not parcellated.
    Returns:
        A connectivity matrix as a numpy array.
    """
    if not files:
        raise ValueError("No files provided.")

    if parcellation_file:
        logger.debug("Loading parcellation data...")
        parcellation = nib.load(parcellation_file)
        parcellation_data = _get_nifti_gifti_data(parcellation).flatten()
    else:
        parcellation_data = None

    for index, filename in enumerate(files):
        logger.debug("Processing file %s of %s...", index + 1, len(files))
        timeseries = _get_nifti_gifti_data(nib.load(filename)).squeeze()

        timeseries_permuted = np.swapaxes(timeseries, 0, -1)
        timeseries_2d = timeseries_permuted.reshape(timeseries_permuted.shape[0], -1)

        if parcellation_data is not None:
            timeseries_2d = _parcellate_timeseries(timeseries_2d, parcellation_data)

        correlation_matrix = np.corrcoef(timeseries_2d, rowvar=False)
        z_matrix = np.arctanh(correlation_matrix)

        if index == 0:
            group_z_matrix = z_matrix / len(files)
        else:
            group_z_matrix += z_matrix / len(files)

    return np.tanh(group_z_matrix)


def _parcellate_timeseries(
    timeseries: npt.ArrayLike, parcellation: npt.ArrayLike
) -> np.ndarray:
    """Parcellate timeseries.

    Args:
        timeseries: Timeseries data in a time-by-region 2D array.
        parcellation: Parcellation data in a 1D vector.

    Returns:
        Parcellated timeseries into a time-by-parcel 2D array.
    """
    logger.debug("Parcellating timeseries...")

    if np.shape(timeseries)[1] != np.size(parcellation):
        raise exceptions.InputError(
            "Parcellation dimensions do not match timeseries dimensions."
        )

    parcellated_timeseries = brainspace_parcellation.reduce_by_labels(
        np.array(timeseries), np.array(parcellation)
    )

    return parcellated_timeseries


def _get_nifti_gifti_data(image: filebasedimages.FileBasedImage) -> np.ndarray:
    """Get the data from a NIfTI or GIFTI image.

    Args:
        image: A NIfTI or GIFTI image.

    Returns:
        The image data as a numpy array.
    """
    if isinstance(image, nib.Nifti1Image):
        logger.debug("Loading NIfTI data...")
        return image.get_fdata()
    if isinstance(image, nib.GiftiImage):
        logger.debug("Loading GIFTI data...")
        return image.darrays[0].data
    raise exceptions.InputError("Input image must be a NIfTI or GIFTI image.")
