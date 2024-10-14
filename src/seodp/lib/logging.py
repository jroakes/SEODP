"""Logging configuration for the SEO Data Platform."""

# import sys
from loguru import logger

# Configure logging to write to both console and a local file
logger.add("seo-dp.log", rotation="1 week", level="INFO")
#logger.add(sys.stderr, level="INFO")