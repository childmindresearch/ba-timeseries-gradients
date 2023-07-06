""" Logging module for grag-brainspace. 

This module provides a logger for the grag-brainspace package.
The logger is imported into other modules using the following snippet:
```python
import logging
from grag_brainspace import logs

LOGGER_NAME = logs.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)
```
"""
import logging
import pathlib

LOGGER_NAME = pathlib.Path(__file__).parent.name
logger = logging.getLogger(LOGGER_NAME)

cf = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
cf.setFormatter(formatter)
logger.addHandler(cf)
