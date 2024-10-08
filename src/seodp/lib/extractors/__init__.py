"""Module that provides a unified interface for extracting data from various sources."""

from lib.extractors.url import SEOContentExtractor
from lib.extractors.gsc import GSCExtractor
from lib.extractors.ga4 import GA4Extractor
from lib.extractors.psi import PSIExtractor
from copy import deepcopy
from typing import Dict

class ExtractorTools:
    """
    A class that provides a unified interface for extracting data from various sources.
    """

    def __init__(self, config: Dict):
        self.config = config
        self.tools = {
            'Google Analytics': GA4Extractor,
            'Search Console': GSCExtractor,
            'URL': SEOContentExtractor,
            'Page Speed Insights': PSIExtractor
        }

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
        config = deepcopy(self.config)

        # Update config with prior_start_date and prior_end_date if provided
        if start_date:
            config.start_date = start_date
        if end_date:
            config.end_date = end_date

        for tool_name, tool_class in self.tools.items():
            tool = tool_class(config)
            tool.authenticate()
            data[tool_name] = tool.extract_data(url)
        return data