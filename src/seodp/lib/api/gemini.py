"""Gemini API client"""

import google.generativeai as genai
from google.generativeai import GenerativeModel, GenerationConfig
from lib.logging import logger
from lib.exceptions import GeminiAPIError

class GeminiAPIClient:
    def __init__(self, config):
        self.config = config
        genai.configure(api_key=config.api['gemini_api_key'])
        self.model = GenerativeModel(model_name=config.gemini_model)

    def generate_content(self, prompt, response_schema=None, temperature=0.2, top_p=1, top_k=1, max_output_tokens=2048):
        """Generate content using the Gemini API."""
        generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json", 
            response_schema=response_schema
        )

        try:
            response = self.model.generate_content(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini API: {str(e)}")
            raise GeminiAPIError(f"Error generating content with Gemini API: {str(e)}")