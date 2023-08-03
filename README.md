# ba-timeseries-gradients

[![Build](https://github.com/cmi-dair/ba-timeseries-gradients/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/cmi-dair/ba-timeseries-gradients/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/cmi-dair/ba-timeseries-gradients/branch/main/graph/badge.svg?token=22HWWFWPW5)](https://codecov.io/gh/cmi-dair/ba-timeseries-gradients)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![L-GPL License](https://img.shields.io/badge/license-L--GPL-blue.svg)](LICENSE)

This is a command line interface (CLI) for running BrainSpace on BIDS-compliant datasets. Gradients are computed for volumetric files in NIFTI format, or surface files in GIFTI format. For more details on BrainSpace, see the [BrainSpace documentation](https://brainspace.readthedocs.io/en/latest/).

## Installation

For local installation the recommended approach is through Poetry. To install through Poetry, run the following commands:

```bash
pip install poetry
poetry install
```

## Usage

The basic usage of the ba_timeseries_gradients CLI is as follows for Poetry-based installations:

```bash
ba_timeseries_gradients [OPTIONS] BIDS_DIR OUTPUT_DIR ANALYSIS_LEVEL
```

The `BIDS_DIR` is the path to the BIDS directory containing the dataset to be analyzed. The `OUTPUT_DIR` is the path to the directory where the output will be saved. The `ANALYSIS_LEVEL` is the level of analysis to be performed, which can currently only be `group`.

For a full list of options, see:

```bash
ba_timeseries_gradients --help
```

It is highly recommended to include options to filter the dataset for specific files. See the BIDS arguments section in the help for more details.

You can also run the CLI through Docker. To do so, run the following command:

```bash
docker run \
    --volume LOCAL_BIDS_DIR:BIDS_DIR \
    --volume LOCAL_OUTPUT_DIR:OUTPUT_DIR \
    ghcr.io/cmi-dair/ba-timeseries-gradients:main \
    [OPTIONS] BIDS_DIR OUTPUT_DIR ANALYSIS_LEVEL
```

Similarly, the CLI can also be run in Singularity as follows:

```bash
singularity run \
    --bind LOCAL_BIDS_DIR:BIDS_DIR \
    --bind LOCAL_OUTPUT_DIR:OUTPUT_DIR \
    docker://ghcr.io/cmi-dair/ba-timeseries-gradients:main \
    [OPTIONS] BIDS_DIR OUTPUT_DIR ANALYSIS_LEVEL
```
