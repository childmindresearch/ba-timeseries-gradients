# /usr/bin/env python
""" Command line interface for ba_timeseries_gradients. """
import argparse
import logging
import pathlib

import bids

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
    output_file = args.output_dir / ("gradients." + args.output_format)

    if args.dry_run:
        logger.info("Detected input files:\n%s", "\n".join(files))
        logger.info("Output file: %s", output_file)
        return

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

    logger.info("Saving gradient map to %s.", output_file)
    utils.save(output_gradients, lambdas, output_file)


def _get_parser() -> argparse.ArgumentParser:
    """
    Returns an ArgumentParser object with the command line arguments for the ba_timeseries_gradients CLI.

    Returns:
        argparse.ArgumentParser: An ArgumentParser object with the command line arguments.

    Notes:
        Arguments in the bids_group must have a `dest` value equivalent to `bids_<argument>`, where
        <argument> is the name of the argument in the BIDS specification.
    """
    parser = argparse.ArgumentParser(
        prog="ba_timeseries_gradients",
        description="""Computes gradients for a BIDS dataset. If the target
        files are volumetric, they must be in NIFTI format, and a parcellation
        file must be provided.""",
        epilog="""Issues can be reported at: https://github.com/cmi-dair/ba_timeseries_gradients.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        choices=["group"],
    )
    bids_group.add_argument(
        "--subject",
        required=False,
        default=None,
        type=str,
        action="append",
        dest="bids_subject",
        help="The subject regex to use for searching BIDS files.",
    )
    bids_group.add_argument(
        "--session",
        required=False,
        default=None,
        type=str,
        action="append",
        dest="bids_session",
        help="The session to include for finding BIDS files.",
    )
    bids_group.add_argument(
        "--suffix",
        required=False,
        default="bold",
        type=str,
        dest="bids_suffix",
        help="Suffix to use for finding BIDS files.",
    )
    bids_group.add_argument(
        "--run",
        required=False,
        default=None,
        type=int,
        action="append",
        dest="bids_run",
        help="The runs to include, may be supplied multiple times.",
    )
    bids_group.add_argument(
        "--task",
        required=False,
        default=None,
        type=str,
        action="append",
        dest="bids_task",
        help="The tasks to include, may be supplied multiple times.",
    )
    bids_group.add_argument(
        "--space",
        required=False,
        default=None,
        type=str,
        dest="bids_space",
        help="The space to use for finding BIDS files.",
    )
    bids_group.add_argument(
        "--extension",
        required=False,
        default=".nii.gz",
        type=str,
        dest="bids_extension",
        help="Extension to use for finding BIDS files.",
    )
    bids_group.add_argument(
        "--datatype",
        required=False,
        default=None,
        type=str,
        dest="bids_datatype",
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
        help="Verbosity level. Must be one of: 10 (DEBUG), 20 (INFO), 30 (WARNING), 40 (ERROR), 50 (CRITICAL).",
    )
    other_group.add_argument(
        "--output_format",
        required=False,
        default="h5",
        type=str,
        help="Output file format",
        choices=["h5", "json"],
    )
    other_group.add_argument(
        "--dry-run",
        required=False,
        action="store_true",
        help="Do not run the pipeline, only show what input files would be used. Note that dry run is logged at the logging.INFO level.",
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


def _get_bids_files(args: argparse.Namespace) -> list[str]:
    """
    Get the list of input files from the BIDS directory.

    Args:
        args: The parsed command-line arguments.

    Returns:
        list[str]: The list of input files.
    """
    search_args = {
        key.replace("bids_", ""): value
        for key, value in args.__dict__.items()
        if key.startswith("bids_") and key != "bids_dir" and value
    }

    layout = bids.BIDSLayout(args.bids_dir, validate=False)
    files = layout.get(return_type="filename", **search_args)

    logger.info("Found %d input files.", len(files))
    logger.debug("Input files: %s", files)

    return files


if __name__ == "__main__":
    main()
