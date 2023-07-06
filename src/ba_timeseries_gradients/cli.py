# /usr/bin/env python
""" Command line interface for ba_timeseries_gradients. """
import argparse
import logging
import pathlib

import bids2table

from ba_timeseries_gradients import exceptions, gradients, logs, utils

LOGGER_NAME = logs.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def main():
    """
    The main function that runs the ba_timeseries_gradients command line interface.
    """
    logger.debug("Parsing command line arguments...")
    parser = _get_parser()
    args = parser.parse_args()

    logger.setLevel(args.verbose)

    logger.debug("Getting input files...")
    files = _get_bids_files(args)

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

    logger.info("Saving gradient map to %s...", args.output_dir)
    utils.save(output_gradients, lambdas, args)


def _get_parser() -> argparse.ArgumentParser:
    """
    Returns an ArgumentParser object with the command line arguments for the ba_timeseries_gradients CLI.

    Returns:
        argparse.ArgumentParser: An ArgumentParser object with the command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="ba_timeseries_gradients",
        description="""Computes gradients for a BIDS dataset. If the target
        files are volumetric, they must be in NIFTI format, and a parcellation
        file must be provided.""",
        epilog="""Issues can be reported at: https://github.com/cmi-dair/ba_timeseries_gradients.""",
    )

    mandatory_group = parser.add_argument_group("Mandatory arguments")
    bids_group = parser.add_argument_group("BIDS arguments")
    brainspace_group = parser.add_argument_group("BrainSpace arguments")
    other_group = parser.add_argument_group("Other arguments")

    mandatory_group.add_argument(
        "bids_dir",
        type=pathlib.Path,
        help="BIDS directory containing the input files.",
    )
    mandatory_group.add_argument(
        "output_dir",
        type=pathlib.Path,
        help="Output directory.",
    )
    mandatory_group.add_argument(
        "analysis_level",
        type=str,
        help="Level of the analysis that will be performed.",
    )
    bids_group.add_argument(
        "--subject",
        required=False,
        default=None,
        type=str,
        action="append",
        dest="sub",
        help="The subject to include for finding BIDS files. Defaults to all subjects.",
    )
    bids_group.add_argument(
        "--session",
        required=False,
        default=None,
        type=int,
        action="append",
        dest="ses",
        help="The session to include for finding BIDS files. Defaults to all sessions.",
    )
    bids_group.add_argument(
        "--suffix",
        required=False,
        default="bold",
        type=str,
        help="Suffix to use for finding BIDS files. Defaults to 'bold'.",
    )
    bids_group.add_argument(
        "--run",
        required=False,
        default=None,
        type=int,
        action="append",
        help="The runs to include, may be supplied multiple times. Defaults to all runs.",
    )
    bids_group.add_argument(
        "--task",
        required=False,
        default=None,
        type=str,
        action="append",
        help="The tasks to include, may be supplied multiple times. Defaults to all tasks.",
    )
    bids_group.add_argument(
        "--extension",
        required=False,
        default=".nii.gz",
        type=str,
        dest="ext",
        help="Extension to use for finding BIDS files. Defaults to '.nii.gz'.",
    )
    bids_group.add_argument(
        "--datatype",
        required=False,
        default=None,
        type=str,
    )
    brainspace_group.add_argument(
        "--parcellation",
        required=False,
        default=None,
        type=pathlib.Path,
        help="Parcellation to use for similarity calculation. Must be a GIFTI or NIFTI file, obligatory if input files are NIFTI.",
    )
    brainspace_group.add_argument(
        "--dimensionality_reduction",
        required=False,
        default="dm",
        type=str,
        help="Dimensionality reduction method to use. Must be one of 'pca', 'le', or 'dm'.",
    )
    brainspace_group.add_argument(
        "--kernel",
        required=False,
        default="cosine",
        type=str,
        help="Kernel to use for similarity calculation. Must be one of: 'pearson', 'spearman', 'cosine', 'normalized_angle', 'gaussian'.",
    )
    brainspace_group.add_argument(
        "--sparsity",
        required=False,
        default=0.9,
        type=float,
        help="Sparsity to use for similarity calculation. Must be a float between 0 and 1.",
    )
    brainspace_group.add_argument(
        "--n_components",
        required=False,
        default=10,
        type=int,
        help="Number of components to use for dimensionality reduction. Must be an integer.",
    )
    other_group.add_argument(
        "--force",
        required=False,
        action="store_true",
        help="Force overwrite of output file if it already exists.",
    )
    other_group.add_argument(
        "--verbose",
        required=False,
        default=logging.INFO,
        type=int,
        help="Verbosity level. Must be one of: 10 (DEBUG), 20 (INFO), 30 (WARNING), 40 (ERROR), 50 (CRITICAL). Defaults to 10.",
    )
    other_group.add_argument(
        "--output_format",
        required=False,
        default="hdf5",
        type=str,
        help="Output format. Must be one of: 'hdf5', or 'json'. Defaults to 'hdf5'.",
    )
    return parser


def _raise_invalid_input(args: argparse.Namespace, files: list[str]) -> None:
    """
    Check if the input arguments are valid.

    Args:
        args: The parsed command-line arguments.
        files: The list of input files.

    Raises:
        InputError: If the output file already exists and the force flag is not set.
        InputError: If no input files are found.
        InputError: If input files are volume files and no parcellation is provided.
        InputError: If the output format is not one of: 'hdf5', or 'json'.
    """
    if (args.output_dir / "gradients.h5").exists() and not args.force:
        raise exceptions.InputError(
            "Output file already exists. Use --force to overwrite."
        )

    if not files:
        raise exceptions.InputError("No input files found.")

    if args.parcellation is None and files[0].endswith(("nii", "nii.gz")):
        raise exceptions.InputError(
            "Must provide a parcellation if input files are volume files."
        )

    if args.output_format not in ("hdf5", "json"):
        raise exceptions.InputError("Output format must be one of: 'hdf5', or 'json'.")


def _get_bids_files(args: argparse.Namespace) -> list[str]:
    """
    Get the list of input files from the BIDS directory.

    Args:
        args: The parsed command-line arguments.

    Returns:
        list[str]: The list of input files.
    """
    bids_keys = {"subject", "session", "suffix", "run", "task", "extension"}
    search_args = {
        key: value
        for key, value in vars(args).items()
        if value is not None and key in bids_keys
    }

    bids_table = bids2table.bids2table(args.bids_dir)
    for key, value in search_args.items():
        if isinstance(value, list):
            bids_table = bids_table[bids_table[key].isin(value)]
        else:
            bids_table = bids_table[bids_table[key] == value]

    files = bids_table["file_path"].tolist()

    logger.info("Found %d files in BIDS directory.", len(files))
    logger.debug("Files: %s", files)
    return files


if __name__ == "__main__":
    main()
