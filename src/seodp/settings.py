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
    'site_url': 'https://www.example.com/',
    'property_id': '123456789',  # Your GA4 property ID
    'page_url': '/example-page/',
    'start_date': '2023-01-01',
    'end_date': '2023-12-31',
    'api': {
        'service_account_file': get_required_env('SERVICE_ACCOUNT_FILE_PATH'),
        'subject_email': get_required_env('SUBJECT_EMAIL'),
        'scrapingbee_api_key': get_required_env('SCRAPINGBEE_API_KEY')
    }
})
