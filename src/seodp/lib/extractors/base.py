"""Base class for all data extractors"""

from abc import ABC, abstractmethod
from lib.exceptions import AuthenticationError

class DataExtractor(ABC):
    def __init__(self):
        self.is_authenticated = False
        self.start_date = None
        self.end_date = None

    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def extract_data(self, **kwargs):
        pass

    def set_date_range(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def check_authentication(self):
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required before extracting data")