"""Google Analytics 4 data extractor."""

from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from lib.extractors.base import DataExtractor

class GA4Extractor(DataExtractor):
    def __init__(self, service_account_file, subject_email):
        super().__init__()
        self.service_account_file = service_account_file
        self.subject_email = subject_email
        self.credentials = None
        self.ga4_client = None

    def authenticate(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, 
            scopes=['https://www.googleapis.com/auth/analytics.readonly'],
            subject=self.subject_email
        )
        self.ga4_client = BetaAnalyticsDataClient(credentials=self.credentials)
        self.is_authenticated = True

    def extract_data(self, property_id, page_url, start_date, end_date):
        self.check_authentication()
        def run_report(metrics, dimensions):
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimension_filter={
                    "filter": {
                        "field_name": "pagePathPlusQueryString",
                        "string_filter": {"value": page_url}
                    }
                }
            )
            response = self.ga4_client.run_report(request)
            return response

        previous_pages = run_report(
            metrics=["screenPageViews"],
            dimensions=["previousPagePath"]
        )

        next_pages = run_report(
            metrics=["screenPageViews"],
            dimensions=["nextPagePath"]
        )

        bounce_rate = run_report(
            metrics=["bounceRate"],
            dimensions=[]
        )

        referring_sites = run_report(
            metrics=["sessions"],
            dimensions=["source"]
        )

        return {
            "previous_pages": [row.dimension_values[0].value for row in previous_pages.rows[:5]],
            "next_pages": [row.dimension_values[0].value for row in next_pages.rows[:5]],
            "bounce_rate": bounce_rate.rows[0].metric_values[0].value if bounce_rate.rows else None,
            "referring_sites": [row.dimension_values[0].value for row in referring_sites.rows[:5]]
        }
