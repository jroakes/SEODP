"""Handles Execution of Processes"""

import json
from datetime import datetime
from .url import URLManager
from .data import DataManager
from .aggregation import AggregationManager
from .llm import LLMManager
from lib.api.email import EmailHandler
from typing import Dict, Any, List

class Manager:
    def __init__(self, config: Dict):
        self.config = config
        self.url_processor = URLManager(config)
        self.data_manager = DataManager(config)
        self.aggregation_manager = AggregationManager(config)
        self.llm_manager = LLMManager(config)
        self.email_handler = EmailHandler(config)

    def run_schedule(self, email_handler: EmailHandler):
        all_insights = self.url_processor.process_all_urls()
        aggregated_insights = self.aggregation_manager.aggregate_insights(all_insights)
        report_content = self.email_handler.format_report(aggregated_insights)
        self.email_handler.send_report(self.config.recipient_email, "SEO Insights Report", report_content)

    def run_test(self, url: str) -> Dict[str, Any]:
        current_data = self.data_manager.get_current_data_live(url)
        prior_data = self.data_manager.get_prior_data_live(url)
        analysis = self.llm_manager.generate_structured_insights(current_data, prior_data)
        return analysis

    def run_single_url(self, url: str):
        current_data = self.data_manager.extract_data(url)
        prior_data = self.data_manager.get_prior_data(url)
        insights = self.llm_manager.generate_structured_insights(current_data, prior_data)
        self.data_manager.store_data(url, datetime.now().strftime('%Y-%m-%d'), current_data, insights)
        return insights

    def run_sitemap_test(self) -> Dict[str, Any]:
        all_insights = []
        for url in self.config.test_sitemap_urls:
            current_data = self.data_manager.get_current_data_live(url)
            prior_data = self.data_manager.get_prior_data_live(url)
            insights = self.llm_manager.generate_structured_insights(current_data, prior_data)
            all_insights.append({"url": url, "insights": insights})

        aggregated_insights = self.aggregation_manager.aggregate_insights(all_insights)
        return aggregated_insights