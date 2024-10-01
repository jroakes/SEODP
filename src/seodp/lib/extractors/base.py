"""Base class for all data extractors"""

from abc import ABC, abstractmethod
from lib.errors import AuthenticationError

class DataExtractor(ABC):
    def __init__(self):
        self.is_authenticated = False

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def extract_data(self, **kwargs):
        pass

    def check_authentication(self):
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required before extracting data")
