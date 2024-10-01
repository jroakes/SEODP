"""Google Search Console data extractor module."""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from lib.extractors.base import DataExtractor

class GSCExtractor(DataExtractor):
    def __init__(self, service_account_file, subject_email):
        super().__init__()
        self.service_account_file = service_account_file
        self.subject_email = subject_email
        self.credentials = None
        self.search_console_service = None

    def authenticate(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, 
            scopes=['https://www.googleapis.com/auth/webmasters.readonly'],
            subject=self.subject_email
        )
        self.search_console_service = build('searchconsole', 'v1', credentials=self.credentials)
        self.is_authenticated = True

    def extract_data(self, site_url, page_url, start_date, end_date):
        self.check_authentication()
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['query'],
            'rowLimit': 10,
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': page_url
                }]
            }]
        }
        response = self.search_console_service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        return {
            "ranking_keywords": [row['keys'][0] for row in response.get('rows', [])]
        }