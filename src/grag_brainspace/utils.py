""" Utility functions for the GRAG BrainSpace package. """
import argparse
import json
import pathlib

import h5py
import numpy as np

from grag_brainspace import exceptions


def save(
    output_gradients: np.ndarray, lambdas: np.ndarray, args: argparse.Namespace
) -> None:
    """
    Saves a numpy array to a file with the given filename.

    Args:
        output_gradients: The numpy array to save.
        filename: The filename to save the array to.

    """
    extension = "h5" if args.output_format == "hdf5" else args.output_format
    filename = args.output_dir / f"gradients.{extension}"

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
    Saves a numpy array to a file with the given filename.

    Args:
        output_gradients: The numpy array to save.
        filename: The filename to save the array to.

    """
    with h5py.File(filename, "w") as fb:
        fb.create_dataset("gradients", data=output_gradients)
        fb.create_dataset("lambdas", data=lambdas)


def save_json(
    output_gradients: np.ndarray, lambdas: np.ndarray, filename: str | pathlib.Path
) -> None:
    """
    Saves a numpy array to a file with the given filename.

    Args:
        output_gradients: The numpy array to save.
        filename: The filename to save the array to.

    """
    with open(filename, "w", encoding="utf-8") as fb:
        json.dump(
            {
                "gradients": output_gradients.tolist(),
                "lambdas": lambdas.tolist(),
            },
            fb,
        )
