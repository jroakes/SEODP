"""Aggregation and processing module for SEO insights with configurable topics and significance threshold."""

from typing import Dict, Any, List
from loguru import logger

def calculate_percentage_change(current: float, previous: float) -> float:
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100

class AggregationManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.report_topics = config.get('report_topics', [])
        self.significance_threshold = config.get('report_significance_threshold', 25)
        self.max_insights = config.get('max_insights', 5)

    def aggregate_insights(self, all_url_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates and prioritizes insights from multiple URLs based on configured topics."""
        aggregated_insights = {
            "total_urls_analyzed": len(all_url_insights),
        }

        for topic in self.report_topics:
            key = topic.lower().replace(' ', '_')
            aggregated_insights[key] = []

        for url_insight in all_url_insights:
            url = url_insight.get("url", "Unknown URL")
            insights = url_insight.get("insights", {})
            
            for topic in self.report_topics:
                key = topic.lower().replace(' ', '_')
                topic_insights = insights.get(key, [])
                self._process_topic_insights(aggregated_insights[key], topic_insights, url)

        self._prioritize_insights(aggregated_insights)
        return aggregated_insights

    def _process_topic_insights(self, aggregated_list: List[Dict[str, Any]], topic_insights: List[Dict[str, Any]], url: str):
        """Process insights for a specific topic."""
        for insight in topic_insights:
            current_value = insight.get('current_value', 0)
            prior_value = insight.get('prior_value', 0)
            change_percentage = calculate_percentage_change(current_value, prior_value)
            change_absolute = current_value - prior_value
            
            if abs(change_absolute) >= self.significance_threshold:
                aggregated_list.append({
                    **insight,
                    "url": url,
                    "change_percentage": change_percentage,
                    "change_absolute": change_absolute
                })

    def _prioritize_insights(self, aggregated_insights: Dict[str, Any]):
        """Prioritize insights based on importance score and limit to max_insights per category."""
        for key in aggregated_insights:
            if isinstance(aggregated_insights[key], list):
                aggregated_insights[key] = sorted(
                    aggregated_insights[key],
                    key=lambda x: x.get("importance_score", 0),
                    reverse=True
                )[:self.max_insights]