"""Custom exceptions for the SEO-DP library."""

class AuthenticationError(Exception):
    pass

class GeminiAPIError(Exception):
    """Raised when there is an error communicating with the Gemini API."""
    pass

class DataManagerError(Exception):
    """Raised when there is an error in the DataManager class."""
    pass

class DataExtractionError(Exception):
    """Raised when there is an error extracting data from a source."""
    pass

class DataProcessingError(Exception):
    """Raised when there is an error processing data."""
    pass

class ConfigurationError(Exception):
    """Raised when there's a problem with the configuration."""
    pass