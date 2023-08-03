"""The parser module for the ba_timeseries_gradients CLI."""
import argparse
import pathlib


def get_parser() -> argparse.ArgumentParser:
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
        type=_path_exists,
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
        type=str,
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
        type=_path_exists,
        help="Parcellation to use for similarity calculation. Must be a GIFTI or NIFTI file, obligatory if input files are NIFTI.",
    )
    brainspace_group.add_argument(
        "--dimensionality_reduction",
        required=False,
        default="dm",
        type=str,
        help="Dimensionality reduction method to use.",
        choices=["pca", "le", "dm"],
    )
    brainspace_group.add_argument(
        "--kernel",
        required=False,
        default="cosine",
        type=str,
        help="Kernel to use for similarity calculation.",
        choices=["pearson", "spearman", "cosine", "normalized_angle", "gaussian"],
    )
    brainspace_group.add_argument(
        "--sparsity",
        required=False,
        default=0.9,
        type=_is_between_zero_and_one,
        help="Sparsity to use for similarity calculation. Must be a float between 0 and 1.",
    )
    brainspace_group.add_argument(
        "--n_components",
        required=False,
        default=10,
        type=_is_positive_integer,
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
        default="info",
        type=str,
        help="Verbosity level.",
        choices=["debug", "info", "warning", "error", "critical"],
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


def _path_exists(path_str: str) -> pathlib.Path:
    """Checks if an argument is an existing path.

    Args:
        path_str: The path to check.

    Returns:
        pathlib.Path: The path as a pathlib.Path if it exists.
    """
    path = pathlib.Path(path_str)
    if path.exists():
        return path
    raise argparse.ArgumentTypeError(f"{path} does not exist.")


def _is_between_zero_and_one(val: str) -> float:
    """Checks if an argument is between 0 and 1.

    Args:
        val: The argument to check.

    Returns:
        float: The argument as a float if it is between 0 (inclusive) and 1 (exclusive).
    """
    if 0 <= float(val) < 1:
        return float(val)
    raise argparse.ArgumentTypeError(f"{val} is not in range [0, 1).")


def _is_positive_integer(value: str) -> int:
    """Checks if an argument is greater than 0.

    Args:
        val: The argument to check.

    Returns:
        float: The argument as a float if it is greater than 0.
    """
    if value.isdigit() and int(value) > 0:
        return int(value)
    raise argparse.ArgumentTypeError("Argument is not a positive integer.")
