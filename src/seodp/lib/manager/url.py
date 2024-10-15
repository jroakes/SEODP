"""URL Manager module."""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from loguru import logger
from lib.manager.data import DataManager
from lib.manager.llm import LLMManager

class URLManager:
    def __init__(self, config: Dict):
        self.config = config
        self.data_manager = DataManager(config)
        self.llm_manager = LLMManager(config)

    def process_all_urls(self) -> List[Dict[str, Any]]:
        urls = self._get_urls()
        all_insights = []
        current_period = self.data_manager.get_current_period()

        for url in urls:

            if not self.data_manager.is_url_excluded_from_processing(url):
                logger.info(f"Processing {url}")
                current_data = self.data_manager.get_current_data_live(url)
                prior_data = self.data_manager.get_prior_data_db(url)
                
                if not prior_data:
                    prior_data = self.data_manager.get_prior_data_live(url)
                    prior_period = self.data_manager.get_prior_period()
                    self.data_manager.store_data(url, prior_period, prior_data, {})
                
                insights = self.llm_manager.generate_structured_insights(current_data, prior_data)
                self.data_manager.store_data(url, current_period, current_data, insights)
                all_insights.append({"url": url, "insights": insights})
            else:
                logger.info(f"Skipping excluded URL: {url}")

        self.data_manager.exclude_low_traffic_urls_from_processing(urls)

        return all_insights

    def _get_urls(self) -> List[str]:
        if hasattr(self.config, 'sitemap_urls') and self.config.sitemap_urls:
            logger.info("Using sitemap URLs from configuration.")
            return self.config.sitemap_urls
        elif hasattr(self.config, 'sitemap_file') and self.config.sitemap_file:
            logger.info("Using sitemap file.")
            return self.extract_urls_from_sitemap(self.config.sitemap_file)
        else:
            raise ValueError("No sitemap URLs or file provided in configuration.")

    @staticmethod
    def extract_urls_from_sitemap(sitemap_source: str) -> List[str]:
        urls = []
        try:
            if sitemap_source.startswith(('http://', 'https://')):
                # Fetch sitemap from URL
                response = requests.get(sitemap_source)
                response.raise_for_status()  # Raise an exception for bad status codes
                root = ET.fromstring(response.content)
            else:
                # Parse local file
                tree = ET.parse(sitemap_source)
                root = tree.getroot()

            namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for url in root.findall('sitemap:url', namespace):
                loc = url.find('sitemap:loc', namespace)
                if loc is not None:
                    urls.append(loc.text)
        except requests.RequestException as e:
            logger.error(f"Error fetching sitemap from URL: {e}")
        except ET.ParseError as e:
            logger.error(f"Error parsing sitemap: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return urls