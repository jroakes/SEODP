"""Logging configuration for the SEO Data Platform."""

# import sys
from loguru import logger


def setup() -> None:
    """Configures logging."""
    # Write logs to a file and to stderr
    logger.add("seo-dp.log", rotation="1 week", level="INFO")
    # logger.add(sys.stderr, level="INFO")
