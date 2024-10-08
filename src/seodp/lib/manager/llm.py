"""LLM module for SEO Data Platform."""

import json
from typing import Dict, Any
from lib.api.gemini import GeminiAPIClient

class LLMManager:
    def __init__(self, config: Dict):
        self.config = config
        self.gemini_client = GeminiAPIClient(config)

    def generate_structured_insights(self, current_data: Dict[str, Any], prior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates structured insights by comparing current and prior data.
        
        This function prepares a prompt with the current and prior data, sends it to the Gemini API,
        and processes the response to extract structured insights.
        
        Args:
            current_data: A dictionary containing the current SEO data.
            prior_data: A dictionary containing the prior SEO data.

        Returns:
            A dictionary containing structured insights.
        """
        prompt = self._create_insight_prompt(current_data, prior_data)
        response_schema = {
            "type": "object",
            "properties": {
                "traffic_change": {
                    "type": "object",
                    "properties": {
                        "direction": {"type": "string", "enum": ["increased", "decreased", "no_change"]},
                        "percentage": {"type": "number"},
                        "analysis": {"type": "string"}
                    },
                    "required": ["direction", "percentage", "analysis"]
                },
                "ranking_changes": {
                    "type": "object",
                    "properties": {
                        "direction": {"type": "string", "enum": ["improved", "declined", "no_change"]},
                        "analysis": {"type": "string"}
                    },
                    "required": ["direction", "analysis"]
                },
                "page_speed_changes": {
                    "type": "object",
                    "properties": {
                        "direction": {"type": "string", "enum": ["improved", "declined", "no_change"]},
                        "analysis": {"type": "string"}
                    },
                    "required": ["direction", "analysis"]
                },
                "critical_issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["type", "description"]
                    }
                },
                "opportunities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["type", "description"]
                    }
                },
                "overall_analysis": {"type": "string"}
            },
            "required": ["traffic_change", "ranking_changes", "page_speed_changes", "critical_issues", "opportunities", "overall_analysis"]
        }
        response = self.gemini_client.generate_content(prompt, response_schema=response_schema)
        return json.loads(response)

    def _create_insight_prompt(self, current_data: Dict[str, Any], prior_data: Dict[str, Any]) -> str:
        """Creates a prompt for the Gemini API to generate SEO insights.

        Args:
            current_data: A dictionary containing the current SEO data.
            prior_data: A dictionary containing the prior SEO data.

        Returns:
            A string containing the formatted prompt for the Gemini API.
        """
        prompt = (
            "Analyze the following SEO data and provide structured insights:\n\n"
            "**Current Data:**\n```json\n"
            f"{json.dumps(current_data, indent=4)}\n"
            "```\n\n"
            "**Prior Data:**\n```json\n"
            f"{json.dumps(prior_data, indent=4)}\n"
            "```\n\n"
            "Provide insights in the following structured format:\n"
            "1. Traffic change (increased, decreased, or no change, with percentage and analysis)\n"
            "2. Ranking changes (improved, declined, or no change, with analysis)\n"
            "3. Page speed changes (improved, declined, or no change, with analysis)\n"
            "4. Critical issues (list of issues with type and description)\n"
            "5. Opportunities (list of opportunities with type and description)\n"
            "6. Overall analysis\n\n"
            "Ensure the response is a valid JSON object matching the specified schema."
        )
        return prompt