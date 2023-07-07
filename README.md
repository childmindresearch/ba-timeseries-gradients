# GRAG-BrainSpace

[![Build](https://github.com/cmi-dair/grag-brainspace/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/cmi-dair/grag-brainspace/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/cmi-dair/grag-brainspace/branch/main/graph/badge.svg?token=22HWWFWPW5)](https://codecov.io/gh/cmi-dair/grag-brainspace)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![L-GPL License](https://img.shields.io/badge/license-L--GPL-blue.svg)](LICENSE)

This is a command line interface (CLI) running BrainSpace on BIDS-compliant datasets. Gradients are computed for volumetric files in NIFTI format, or surface files in GIFTI format. For more details on BrainSpace, see the [BrainSpace documentation](https://brainspace.readthedocs.io/en/latest/).

## Installation

A PyPi installation will follow soon. Until then, the recommended approaches for installing grag-brainspace is through Docker. To build it, download the repository and run the following command from the repository root:

```
docker build -t grag-brainspace .
```

## Usage

The basic usage of the grag-brainspace CLI is as follows:

```
docker run grag-brainspace [OPTIONS] BIDS_DIR OUTPUT_DIR ANALYSIS_LEVEL
```

For details on all the options, simply run:

```
docker run grag-brainspace -h
```
