"""Module that provides a unified interface for extracting data from various sources."""

from copy import deepcopy
from typing import Dict
from lib.extractors.ga4 import GA4Extractor
from lib.extractors.gsc import GSCExtractor
from lib.extractors.psi import PSIExtractor
from lib.extractors.url import URLExtractor
from loguru import logger


EXTRACTOR_CLASSES = [GA4Extractor, GSCExtractor, PSIExtractor, URLExtractor]


class ExtractorTools:
    """
    A class that provides a unified interface for extracting data from various sources.
    """

    def __init__(self, config: Dict):
        self.config = config
        self.tools = self._load_extractors(config)


    @staticmethod
    def _load_extractors(config):
        """Dynamically loads all registered data extractors."""
        extractors = {}
        for extractor_class in EXTRACTOR_CLASSES: # Changed entry point group name
            try:
                extractor = extractor_class(config)
                extractors[extractor.name] = extractor
            except Exception as e:
                logger.error(f"Error loading extractor {extractor.name}: {e}")
        return extractors


    def extract_data(self, url: str, start_date: str = None, end_date: str = None) -> Dict[str, Dict]:
        """
        Extract data from various sources for a given URL and date range.

        Args:
            url (str): The URL for which data needs to be extracted.
            start_date (str, optional): The start date for the date range. Defaults to None.
            end_date (str, optional): The end date for the date range. Defaults to None.

        Returns:
            Dict[str, Dict]: A dictionary containing the extracted data, where the keys are the source names and the values are dictionaries containing the extracted data for that source.
        """
        data = {}

        for tool_name, tool in self.tools.items():
            
            # Log tool name, URL, and date range in one line
            logger.info(f"Extracting data from {tool_name} for URL: {url}, start date: {start_date}, end date: {end_date}")
            
            tool.authenticate()
            if start_date and end_date:
                tool.set_date_range(start_date, end_date)
            data[tool_name] = tool.extract_data(url=url)

        return data