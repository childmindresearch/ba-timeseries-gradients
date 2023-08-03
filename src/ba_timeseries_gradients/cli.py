# /usr/bin/env python
""" Command line interface for ba_timeseries_gradients. """
import argparse
import logging

import bids

from ba_timeseries_gradients import exceptions, gradients, logs, parser, utils

LOGGER_NAME = logs.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def main() -> None:
    """
    The main function that runs the ba_timeseries_gradients command line interface.
    """
    logger.debug("Parsing command line arguments...")
    args = parser.get_parser().parse_args()

    logger.setLevel(logging.getLevelName(args.verbose.upper()))

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
    """Get the list of input files from the BIDS directory.

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
    files: list[str] = layout.get(return_type="filename", **search_args)

    logger.info("Found %d input files.", len(files))
    logger.debug("Input files: %s", files)

    return files


if __name__ == "__main__":
    main()
