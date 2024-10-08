import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Any, List
from settings import CONFIG
from lib.logging import logger
from lib.manager.data import DataManager
from lib.manager.llm import LLMManager

class URLManager:
    def __init__(self, config: Dict):
        self.config = config
        self.data_manager = DataManager(config)
        self.llm_manager = LLMManager(config)
        self.schedule = config.schedule
        self.process_interval = timedelta(weeks=1) if self.schedule == 'weekly' else timedelta(days=30)
        self.next_run = self.data_manager.get_last_processing_date() + self.process_interval if self.data_manager.get_last_processing_date() else datetime.now()

    def process_all_urls(self) -> List[Dict[str, Any]]:
        urls = self.extract_urls_from_sitemap(self.config.sitemap_file)
        all_insights = []
        for url in urls:
            if not self.data_manager.is_url_excluded_from_processing(url):
                logger.info(f"Processing {url}")
                current_data = self.data_manager.extract_data(url)
                prior_data = self.data_manager.get_prior_data(url)
                insights = self.llm_manager.generate_structured_insights(current_data, prior_data)
                self.data_manager.store_data(url, datetime.now().strftime('%Y-%m-%d'), current_data, insights)
                all_insights.append({"url": url, "insights": insights})
            else:
                logger.info(f"Skipping excluded URL: {url}")
        
        self.data_manager.exclude_low_traffic_urls_from_processing(urls)
        return all_insights

    def aggregate_insights(self, all_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.data_manager.aggregate_insights(all_insights)

    def extract_urls_from_sitemap(self, sitemap_file: str) -> List[str]:
        urls = []
        try:
            tree = ET.parse(sitemap_file)
            root = tree.getroot()
            namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for url in root.findall('sitemap:url', namespace):
                loc = url.find('sitemap:loc', namespace)
                if loc is not None:
                    urls.append(loc.text)
        except ET.ParseError as e:
            logger.error(f"Error parsing sitemap: {e}")
        return urls