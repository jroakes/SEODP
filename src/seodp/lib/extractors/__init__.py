from lib.extractors.url import SEOContentExtractor
from lib.extractors.gsc import GSCExtractor
from lib.extractors.ga4 import GA4Extractor
from lib.extractors.psi import PSIExtractor
from copy import deepcopy


class ExtractorTools:
    def __init__(self, config):
        self.config = config
        self.tools = {
            'Google Analytics': GA4Extractor,
            'Search Console': GSCExtractor,
            'URL': SEOContentExtractor,
            'Page Speed Insights': PSIExtractor
        }

    def extract_data(self, url, start_date=None, end_date=None):
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