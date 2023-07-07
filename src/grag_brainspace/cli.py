# /usr/bin/env python
""" Command line interface for grag-brainspace. """
import argparse
import logging
import pathlib

import h5py
import numpy as np

from grag_brainspace import exceptions, gradients, logs

LOGGER_NAME = logs.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def main():
    """
    The main function that runs the grag-brainspace command line interface.
    """
    logger.debug("Parsing command line arguments...")
    parser = _get_parser()
    args = parser.parse_args()

    logger.debug("Getting input files...")
    files = args.input_file or _parse_input_list(args.input_list)

    logger.debug("Checking input validity.")
    _raise_invalid_input(args, files)

    logger.info("Calculating gradient map...")
    output_gradients, lambdas = gradients.compute_gradients(
        files,
        parcellation_file=args.parcellation,
        approach=args.dimensionality_reduction,
        kernel=args.kernel,
        n_components=args.n_components,
        sparsity=args.sparsity,
    )

    logger.info("Saving gradient map to %s...", args.output)
    _save_numpy_array(output_gradients, lambdas, filename=args.output)


def _save_numpy_array(
    output_gradients: np.ndarray, lambdas: np.ndarray, filename: str | pathlib.Path
) -> None:
    """
    Saves a numpy array to a file with the given filename.

    Args:
        output_gradients: The numpy array to save.
        filename: The filename to save the array to.

    """
    filepath = pathlib.Path(filename)
    with h5py.File(filepath, "w") as f:
        f.create_dataset("gradients", data=output_gradients)
        f.create_dataset("lambdas", data=lambdas)


def _get_parser() -> argparse.ArgumentParser:
    """
    Returns an ArgumentParser object with the command line arguments for the grag-brainspace CLI.

    Returns:
        argparse.ArgumentParser: An ArgumentParser object with the command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="grag-brainspace",
        description="""Computes gradients for a collection of files. Files must be either
        volumetric or surface files. If the files are volumetric, they must be in NIFTI format,
        and a parcellation file must be provided.""",
        epilog="© 2023 Child Mind Institute",
    )
    parser.add_argument(
        "--input_file",
        "-i",
        nargs="*",
        required=False,
        default=None,
        type=pathlib.Path,
        help="Input file(s) to process. Must be 4D GIFTI or NIFTI files.",
    )
    parser.add_argument(
        "--input_list",
        "-l",
        required=False,
        default=None,
        type=pathlib.Path,
        help="Input file list to process. Must be a text file with one file per line.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=pathlib.Path,
        help="Output gradient filename. Must be HDF5 file.",
    )
    parser.add_argument(
        "--parcellation",
        "-p",
        required=False,
        default=None,
        type=pathlib.Path,
        help="Parcellation to use for similarity calculation. Must be a GIFTI or NIFTI file.",
    )
    parser.add_argument(
        "--dimensionality_reduction",
        "-d",
        required=False,
        default="dm",
        type=str,
        help="Dimensionality reduction method to use. Must be one of 'pca', 'le', or 'dm'.",
    )
    parser.add_argument(
        "--kernel",
        "-k",
        required=False,
        default="cosine",
        type=str,
        help="Kernel to use for similarity calculation. Must be one of: 'pearson', 'spearman', 'cosine', 'normalized_angle', 'gaussian'.",
    )
    parser.add_argument(
        "--sparsity",
        "-s",
        required=False,
        default=0.9,
        type=float,
        help="Sparsity to use for similarity calculation. Must be a float between 0 and 1.",
    )
    parser.add_argument(
        "--n_components",
        "-n",
        required=False,
        default=10,
        type=int,
        help="Number of components to use for dimensionality reduction. Must be an integer.",
    )
    parser.add_argument(
        "--force",
        "-f",
        required=False,
        action="store_true",
        help="Force overwrite of output file if it already exists.",
    )
    return parser


def _parse_input_list(input_list: str | pathlib.Path) -> list[str]:
    """Parse input list.

    Args:
        input_list: Path to input list.

    Returns:
        List of input files.

    Raises:
        InputError: If input list is empty.
        InputError: If not all files in input list exist.
        InputError: If input list contains duplicate files.
    """
    with open(input_list, "r", encoding="utf-8") as fb:
        input_files = fb.read().splitlines()

    if not input_files:
        raise exceptions.InputError("Input list is empty.")

    if not all(pathlib.Path(input_file).exists() for input_file in input_files):
        raise exceptions.InputError(
            "Not all files in input list exist. Please check your input list."
        )

    if len(set(input_files)) != len(input_files):
        raise exceptions.InputError(
            "Input list contains duplicate files. Please check your input list."
        )

    return input_files


def _raise_invalid_input(args: argparse.Namespace, files: list[str]) -> None:
    """
    Check if the input arguments are valid.

    Args:
        args: The parsed command-line arguments.
        files: The list of input files.

    Raises:
        InputError: If neither an input file nor an input list is provided or both are.
        InputError: If the output file already exists and the force flag is not set.
        InputError: If input files are volume files and no parcellation is provided.
        InputError: If input files are not all volume files or not all surface files.
    """
    if (
        (args.input_file is None and args.input_list is None)
        or (args.input_file is not None and args.input_list is not None)
        or not files
    ):
        raise exceptions.InputError(
            "You must provide either an input file or a non-empty input list."
        )

    if pathlib.Path(args.output).exists() and not args.force:
        raise exceptions.InputError(
            "Output file already exists. Please choose a different output file or include the -f flag."
        )

    if not all(
        (str(filename).endswith((".nii", ".nii.gz")) for filename in files)
    ) and not all((str(filename).endswith(".gii") for filename in files)):
        raise exceptions.InputError(
            "Input file(s) must be either be GIFTI or NIFTI files, not both."
        )

    if args.parcellation is None and files[0].endswith(("nii", "nii.gz")):
        raise exceptions.InputError(
            "Must provide a parcellation if input files are volume files."
        )


if __name__ == "__main__":
    main()
