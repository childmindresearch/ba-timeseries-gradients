# ba-timeseries-gradients

[![Build](https://github.com/cmi-dair/ba-timeseries-gradients/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/cmi-dair/ba-timeseries-gradients/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/cmi-dair/ba-timeseries-gradients/branch/main/graph/badge.svg?token=22HWWFWPW5)](https://codecov.io/gh/cmi-dair/ba-timeseries-gradients)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![L-GPL License](https://img.shields.io/badge/license-L--GPL-blue.svg)](LICENSE)

This is a command line interface (CLI) running BrainSpace on BIDS-compliant datasets. Gradients are computed for volumetric files in NIFTI format, or surface files in GIFTI format. For more details on BrainSpace, see the [BrainSpace documentation](https://brainspace.readthedocs.io/en/latest/).

## Installation

The recommended approaches for installing ba-timeseries-gradients is through Docker or PyPi. To build it as a Docker image, download the repository and run the following command from the repository root:

```bash
docker build -t ba_timeseries_gradients .
```

To install through PyPi, run the following command:

```bash
pip install ba_timeseries_gradients
```

## Usage

The basic usage of the ba_timeseries_gradients CLI is as follows, depending on whether you've installed through PyPi or Docker:

```bash
docker run --volume LOCAL_BIDS_DIR:BIDS_DIR --volume LOCAL_OUTPUT_DIR:OUTPUT_DIR ba_timeseries_gradients [OPTIONS] BIDS_DIR OUTPUT_DIR ANALYSIS_LEVEL
ba_timeseries_gradients [OPTIONS] BIDS_DIR OUTPUT_DIR ANALYSIS_LEVEL
```

The `BIDS_DIR` is the path to the BIDS directory containing the dataset to be analyzed. The `OUTPUT_DIR` is the path to the directory where the output will be saved. The `ANALYSIS_LEVEL` is the level of analysis to be performed, which can currently only be `group`.

For a complete list of options see `ba_timeseries_gradients -h`. It is highly recommended to include options to filter the dataset for specific files. See the BIDS arguments section in the help for more details.
