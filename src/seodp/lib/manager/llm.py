"""LLM module for SEO Data Platform with configurable topics and significance threshold."""

import json
from typing import Dict, Any, List
from lib.api.gemini import GeminiAPIClient

from settings import Config


class LLMManager:
    def __init__(self, config: Config):
        self.config = config
        self.gemini_client = GeminiAPIClient(config)
        self.report_topics = config.report_topics
        self.significance_threshold = config.report_significance_threshold

    def generate_structured_insights(self, current_data: Dict[str, Any], prior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates structured insights based on configured topics and significance threshold."""
        prompt = self._create_insight_prompt(current_data, prior_data)
        response_schema = self._create_response_schema()

        # Generate insights using Gemini API
        response = self.gemini_client.generate_content(prompt, response_schema=response_schema)
        insights = json.loads(response)
        
        # Calculate change_percentage and change_absolute for each insight
        for topic in insights:
            for insight in insights[topic]:
                if 'prior_value' in insight and 'current_value' in insight:
                    insight['change_percentage'] = self._calculate_change_percentage(insight['prior_value'], insight['current_value'])
                    insight['change_absolute'] = insight['current_value'] - insight['prior_value']
        
        return insights

    def _calculate_change_percentage(self, prior_value: float, current_value: float) -> float:
        """Calculates the percentage change between two values."""
        if prior_value == 0:
            return 100 if current_value > 0 else 0
        return ((current_value - prior_value) / prior_value) * 100

    def _create_insight_prompt(self, current_data: Dict[str, Any], prior_data: Dict[str, Any]) -> str:
        """Creates a prompt for the Gemini API to generate targeted SEO insights."""
        prompt = f"""
        Analyze the following SEO data and provide insights on the specified topics:

        Current Data:
        {json.dumps(current_data, indent=2)}

        Prior Data:
        {json.dumps(prior_data, indent=2)}

        Focus on the following topics and provide detailed insights:

        {self._format_topics()}

        For each insight:
        - Provide specific data points for both current and prior periods
        - Assign an importance score (0-100) based on the potential impact of the change
        - Provide clear, actionable details about the change
        - Focus on significant changes in absolute values or clear trends

        Ensure all conclusions are strongly supported by the data provided. Focus on changes that have a substantial impact on the URL's performance.
        """
        return prompt

    def _format_topics(self) -> str:
        """Formats the report topics for the prompt."""
        return "\n".join(f"- {topic}" for topic in self.report_topics)

    def _create_response_schema(self) -> Dict[str, Any]:
        """Creates a response schema based on the configured topics."""
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for topic in self.report_topics:
            key = topic.lower().replace(' ', '_')
            schema["properties"][key] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "importance_score": {"type": "number"},
                        "current_value": {"type": "number"},
                        "prior_value": {"type": "number"},
                        "details": {"type": "string"},
                        "change_absolute": {"type": "number"},
                        "change_percentage": {"type": "number"}
                    },
                    "required": ["description", "importance_score", "current_value", "prior_value", "details"]
                }
            }
            schema["required"].append(key)
        
        return schema