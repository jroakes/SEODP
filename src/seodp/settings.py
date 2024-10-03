"""Settings for the SEO Data Platform."""

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class DotDict(dict):
    """
    A dictionary subclass that allows dot notation access to its items.
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class ConfigurationError(Exception):
    """Raised when there's a problem with the configuration."""
    pass

def get_required_env(key: str) -> str:
    """Get a required environment variable or raise an error."""
    value = os.getenv(key)
    if value is None:
        raise ConfigurationError(f"Missing required environment variable: {key}")
    return value

CONFIG = DotDict({
    'site_url': 'https://locomotive.agency/',
    'property_id': '281603923',
    'page_url': 'https://locomotive.agency/local-seo/how-to-handle-local-seo-without-a-physical-address/',
    'start_date': '2024-07-01',
    'end_date': '2024-07-31',
    'low_traffic_threshold': 100,
    'schedule': 'monthly',
    'sitemap_file': 'sitemap.xml',
    'db_file': 'seodp.db',
    'top_n': 10,
    'gemini_model': 'gemini-1.5-pro',  # Added setting for Gemini model
    'api': {
        'service_account_file': get_required_env('SERVICE_ACCOUNT_FILE_PATH'),
        'subject_email': get_required_env('SUBJECT_EMAIL'),
        'scrapingbee_api_key': get_required_env('SCRAPINGBEE_API_KEY'),
        'gemini_api_key': get_required_env('GEMINI_API_KEY')
    }
})

