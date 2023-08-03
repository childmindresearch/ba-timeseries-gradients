""" Utility functions for the BrainSpace runner. """
import json
import pathlib

import h5py
import numpy as np

from ba_timeseries_gradients import exceptions


def save(
    output_gradients: np.ndarray, lambdas: np.ndarray, filename: str | pathlib.Path
) -> None:
    """
    Saves a numpy array to a file with the given filename.

    Args:
        output_gradients: The numpy array to save.
        lambdas: The lambdas to save.
        filename: The filename to save the array to.

    """
    filename = pathlib.Path(filename)
    if filename.suffix == ".h5":
        save_hdf5(output_gradients, lambdas, filename)
    elif filename.suffix == ".json":
        save_json(output_gradients, lambdas, filename)
    else:
        raise exceptions.InternalError(f"Unsupported file type: {filename}")


def save_hdf5(
    output_gradients: np.ndarray, lambdas: np.ndarray, filename: str | pathlib.Path
) -> None:
    """
    Saves a numpy array to a HDF5 file with the given filename.

    Args:
        output_gradients: The numpy array to save.
        filename: The filename to save the array to.

    """
    with h5py.File(filename, "w") as h5_file:
        h5_file.create_dataset("gradients", data=output_gradients)
        h5_file.create_dataset("lambdas", data=lambdas)


def save_json(
    output_gradients: np.ndarray, lambdas: np.ndarray, filename: str | pathlib.Path
) -> None:
    """
    Saves a numpy array to a JSON file with the given filename.

    Args:
        output_gradients: The numpy array to save.
        filename: The filename to save the array to.

    """
    with open(filename, "w", encoding="utf-8") as file_buffer:
        json.dump(
            {
                "gradients": output_gradients.tolist(),
                "lambdas": lambdas.tolist(),
            },
            file_buffer,
        )
