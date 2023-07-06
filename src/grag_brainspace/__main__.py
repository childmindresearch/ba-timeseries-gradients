""" Entry point for the package, when run as `python -m grag_brainspace` """
import logging

from grag_brainspace import cli, logs

LOGGER_NAME = logs.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

if __name__ == "__main__":
    logger.info("Called through __main__.py.")
    cli.main()
