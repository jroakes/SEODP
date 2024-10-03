"""Gemini API client."""

import json
import google.generativeai as genai

class GeminiAPIClient:
    def __init__(self, config):
        self.config = config
        genai.configure(api_key=config.api['gemini_api_key'])
        self.model = genai.GenerativeModel(model_name=config.gemini_model, tools='code_execution')

    @staticmethod
    def _maybe_json_dump(data, indent=4):
        if isinstance(data, dict):
            return json.dumps(data, indent=indent)
        return data
    

    def generate_insights(self, current_data, prior_data):
        """
        Generate insights from the changes between the current and prior data sets.

        Args:
            current_data (dict): The current JSON data set.
            prior_data (dict): The prior JSON data set.

        Returns:
            str: A string containing the generated insights in Markdown format.
        """
        current_data_json = self._maybe_json_dump(current_data)
        prior_data_json = self._maybe_json_dump(prior_data)

        prompt = (
            f'Current data:\n\n```json\n{current_data_json}\n```\n\n'
            f'Prior data:\n\n```json\n{prior_data_json}\n```\n\n'
            'Analyze and compare the current and prior data sets, and provide any interesting insights or observations '
            'regarding the changes between the two in Markdown format. Focus on identifying significant differences, trends, or patterns.'
        )
        response = self.model.generate_content(prompt)
        return response.text
    