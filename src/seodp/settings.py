"""Settings for the SEO Data Platform."""

import os
import yaml
from lib.exceptions import ConfigurationError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class DotDict(dict):
    """
    A dictionary subclass that allows dot notation access to its items.
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def get_required_env(key: str) -> str:
    """Get a required environment variable or raise an error."""
    value = os.getenv(key)
    if value is None:
        raise ConfigurationError(f"Missing required environment variable: {key}")
    return value

def load_config(yaml_file: str) -> DotDict:
    """Load configuration from a YAML file."""
    try:
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
            return DotDict(config)
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {yaml_file}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Error parsing YAML file: {e}")


CONFIG = load_config('seodpconfig.yaml')
CONFIG.api = DotDict({
    'service_account_file': get_required_env('SERVICE_ACCOUNT_FILE_PATH'),
    'subject_email': get_required_env('SUBJECT_EMAIL'),
    'scrapingbee_api_key': get_required_env('SCRAPINGBEE_API_KEY'),
    'gemini_api_key': get_required_env('GEMINI_API_KEY'),
    'mailtrap_login': get_required_env('MAILTRAP_LOGIN'),
    'mailtrap_password': get_required_env('MAILTRAP_PASSWORD'),
    'mailtrap_sender_email': get_required_env('MAILTRAP_SENDER_EMAIL'),
    'recipient_email': get_required_env('RECIPIENT_EMAIL')
})