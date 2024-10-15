"""Google Search Console data extractor module."""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from lib.extractors.base import DataExtractor
from typing import Dict

from settings import Config


class GSCExtractor(DataExtractor):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.service_account_file = config.api.service_account_file
        self.subject_email = config.api.subject_email
        self.credentials = None
        self.search_console_service = None
        self.top_n = config.top_n

    def authenticate(self) -> None:
        """Authenticate with Google Search Console API."""
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/webmasters.readonly'],
            subject=self.subject_email
        )
        self.search_console_service = build('searchconsole', 'v1', credentials=self.credentials)
        self.is_authenticated = True

    def extract_data(self, url: str) -> Dict:
        """Extract Google Search Console data for a given page URL."""
        self.check_authentication()

        overall_request = {
            'startDate': self.start_date,
            'endDate': self.end_date,
            'dimensions': ['page'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': url
                }]
            }]
        }
        overall_response = self.search_console_service.searchanalytics().query(siteUrl=self.config.site_url, body=overall_request).execute()

        query_request = {
            'startDate': self.start_date,
            'endDate': self.end_date,
            'dimensions': ['query'],
            'rowLimit': self.top_n,
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': url
                }]
            }]
        }
        query_response = self.search_console_service.searchanalytics().query(siteUrl=self.config.site_url, body=query_request).execute()

        overall_data = overall_response.get('rows', [{}])[0]

        return {
            "clicks": overall_data.get('clicks', 0),
            "impressions": overall_data.get('impressions', 0),
            "ctr": overall_data.get('ctr', 0),
            "avg_position": overall_data.get('position', 0),
            "ranking_keywords": [
                {
                    "query": row['keys'][0],
                    "clicks": row['clicks'],
                    "impressions": row['impressions'],
                    "ctr": row['ctr'],
                    "position": row['position']
                } for row in query_response.get('rows', [])[:self.top_n]
            ],
            "top_no_click_queries": [
                row['keys'][0] for row in sorted(
                    query_response.get('rows', []),
                    key=lambda x: x['impressions'] - x['clicks'],
                    reverse=True
                )[:self.top_n]
            ]
        }