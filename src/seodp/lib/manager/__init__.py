import json
from typing import Dict, Any, List
from lib.logging import logger
from .url import URLManager
from .data import DataManager
from .aggregation import AggregationManager
from .llm import LLMManager
from lib.api.email import EmailHandler

class Manager:
    def __init__(self, config: Dict):
        self.config = config
        self.url_manager = URLManager(config)
        self.data_manager = DataManager(config)
        self.aggregation_manager = AggregationManager(config)
        self.llm_manager = LLMManager(config)
        self.email_handler = EmailHandler(config)

    def run_schedule(self):
        logger.info("Starting scheduled run")
        all_insights = self.url_manager.process_all_urls()
        current_period = self.data_manager.get_current_period()
        
        aggregated_insights = self.aggregation_manager.aggregate_insights(all_insights)
        report_content = self.email_handler.format_report(aggregated_insights)
        self.email_handler.send_report(report_content)
        
        logger.info("Scheduled run completed")

    def run_url_test(self, url: str) -> Dict[str, Any]:
        logger.info(f"Running URL test for: {url}")
        current_period = self.data_manager.get_current_period()
        prior_period = self.data_manager.get_prior_period()
        
        current_data = self.data_manager.get_current_data_live(url)
        prior_data = self.data_manager.get_prior_data_db(url)
        
        if not prior_data:
            prior_data = self.data_manager.get_prior_data_live(url)
        
        insights = self.llm_manager.generate_structured_insights(current_data, prior_data)
        
        return {
            'url': url, 
            'current_period': current_period, 
            'prior_period': prior_period,
            'current_data': current_data, 
            'prior_data': prior_data,
            'insights': insights
        }

    def run_sitemap_test(self, urls: List[str]) -> Dict[str, Any]:
        logger.info("Running sitemap test")
        all_insights = []
        for url in urls:
            test_result = self.run_url_test(url)
            all_insights.append({"url": url, "insights": test_result['insights']})
        return self.aggregation_manager.aggregate_insights(all_insights)

    def run_email_test(self, recipient_email: str):
        logger.info(f"Running email test for recipient: {recipient_email}")
        with open('example_insights.json', 'r') as f:
            example_insights = json.load(f)
        report_content = self.email_handler.format_report(example_insights)
        self.email_handler.send_report(report_content)
        logger.info("Email test completed")

    def save_results(self, results: Dict[str, Any], output_file: str):
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=4)
            logger.info(f"Results written to {output_file}")
        except IOError as e:
            logger.error(f"Error writing to output file: {e}")