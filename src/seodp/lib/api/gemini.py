"""Gemini API client"""

from typing import Optional, Any, Dict
import google.generativeai as genai
from google.generativeai import GenerativeModel, GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from loguru import logger
from lib.exceptions import GeminiAPIError

from settings import Config


class GeminiAPIClient:
    def __init__(self, config: Config):
        self.config = config
        genai.configure(api_key=config.api.gemini_api_key)
        self.model = GenerativeModel(model_name=config.gemini_model)

    def generate_content(self, prompt: str, response_schema: Optional[Dict[str, Any]] = None, 
                         temperature: float = 0.2, top_p: float = 1, top_k: int = 1, 
                         max_output_tokens: int = 2048) -> str:
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
            response_text = self._make_api_call(prompt, generation_config)
            self._log_token_counts(prompt, response_text)
            return response_text
        except RetryError as e:
            logger.error(f"Gemini API call failed after multiple retries: {str(e)}")
            raise GeminiAPIError(f"Gemini API call failed after multiple retries: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during content generation: {str(e)}")
            raise GeminiAPIError(f"Unexpected error during content generation: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_api_call(self, prompt: str, generation_config: GenerationConfig) -> str:
        """Make the API call to Gemini with retry logic."""
        response = self.model.generate_content(prompt, generation_config=generation_config)
        return response.text

    def _log_token_counts(self, prompt: str, response_text: str) -> None:
        """Log the token counts for the generated content."""
        prompt_tokens = self.model.count_tokens(prompt)
        response_tokens = self.model.count_tokens(response_text)

        logger.info(f"Prompt tokens: {prompt_tokens}")
        logger.info(f"Response tokens: {response_tokens}")