from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension, Filter, FilterExpression
from lib.extractors.base import DataExtractor
from urllib.parse import urlparse, urlunparse
from typing import Dict

from settings import Config


class GA4Extractor(DataExtractor):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.service_account_file = config.api.service_account_file
        self.subject_email = config.api.subject_email
        self.credentials = None
        self.ga4_client = None
        self.top_n = config.top_n

    def authenticate(self) -> None:
        """Authenticate with Google Analytics 4 API."""
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/analytics.readonly'],
            subject=self.subject_email
        )
        self.ga4_client = BetaAnalyticsDataClient(credentials=self.credentials)
        self.is_authenticated = True

    def extract_data(self, url: str) -> Dict:
        """Extract Google Analytics 4 data for a given page URL."""
        self.check_authentication()

        page_path = urlparse(url).path
        page_path = urlunparse(("", "", page_path, "", "", ""))

        def run_report(metrics: list, dimensions: list, filters: FilterExpression = None) -> dict:
            request = RunReportRequest(
                property=f"properties/{self.config.property_id}",
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                date_ranges=[DateRange(start_date=self.start_date, end_date=self.end_date)],
                dimension_filter=filters
            )
            response = self.ga4_client.run_report(request)
            return response

        organic_filter = FilterExpression(
            and_group={
                "expressions": [
                    FilterExpression(
                        filter=Filter(
                            field_name="sessionMedium",
                            string_filter={"value": "organic"}
                        )
                    ),
                    FilterExpression(
                        filter=Filter(
                            field_name="pagePath",
                            string_filter={"value": page_path}
                        )
                    )
                ]
            }
        )

        # Added organic sessions, organic users, and organic new users
        organic_metrics = run_report(
            metrics=["sessions", "totalUsers", "newUsers"],
            dimensions=[],
            filters=organic_filter
        )

        bounce_rate = run_report(
            metrics=["bounceRate"],
            dimensions=[],
            filters=organic_filter
        )

        referring_sites = run_report(
            metrics=["sessions"],
            dimensions=["sessionSource"],
            filters=organic_filter
        )

        avg_time_on_page = run_report(
            metrics=["averageSessionDuration"],
            dimensions=[],
            filters=organic_filter
        )

        user_demographics = run_report(
            metrics=["totalUsers"],
            dimensions=["userAgeBracket", "userGender", "country"],
            filters=FilterExpression(
                filter=Filter(
                    field_name="pagePath",
                    string_filter={"value": page_path}
                )
            )
        )

        device_categories = run_report(
            metrics=["totalUsers"],
            dimensions=["deviceCategory"],
            filters=organic_filter
        )

        pages_leading_to = run_report(
            metrics=["screenPageViews"],
            dimensions=["pageReferrer"],
            filters=organic_filter
        )

        pages_visited_next = run_report(
            metrics=["screenPageViews"],
            dimensions=["pagePath"],
            filters=FilterExpression(
                and_group={
                    "expressions": [
                        FilterExpression(
                            filter=Filter(
                                field_name="pageReferrer",
                                string_filter={"value": url}
                            )
                        ),
                        FilterExpression(
                            filter=Filter(
                                field_name="sessionMedium",
                                string_filter={"value": "organic"}
                            )
                        ),
                    ]
                }
            )
        )

        engagement_rate = run_report(
            metrics=["engagementRate"],
            dimensions=[],
            filters=organic_filter
        )


        revenue = run_report(
            metrics=["totalRevenue"],
            dimensions=[],
            filters=organic_filter
        )

        return {
            "organic_sessions": organic_metrics.rows[0].metric_values[0].value if organic_metrics.rows else None,
            "organic_users": organic_metrics.rows[0].metric_values[1].value if organic_metrics.rows else None,
            "organic_new_users": organic_metrics.rows[0].metric_values[2].value if organic_metrics.rows else None,
            "bounce_rate": bounce_rate.rows[0].metric_values[0].value if bounce_rate.rows else None,
            "referring_sites": [row.dimension_values[0].value for row in referring_sites.rows[:self.top_n]],
            "avg_time_on_page": avg_time_on_page.rows[0].metric_values[0].value if avg_time_on_page.rows else None,
            "engagement_rate": engagement_rate.rows[0].metric_values[0].value if engagement_rate.rows else None,
            "revenue": revenue.rows[0].metric_values[0].value if revenue.rows else None,           
            "user_demographics": [
                {
                    "age": row.dimension_values[0].value,
                    "gender": row.dimension_values[1].value,
                    "country": row.dimension_values[2].value,
                    "users": row.metric_values[0].value
                } for row in user_demographics.rows[:self.top_n]
            ],
            "device_categories": {
                row.dimension_values[0].value: row.metric_values[0].value
                for row in device_categories.rows
            },
            "pages_visited_prior": [
                {
                    "page": row.dimension_values[0].value,
                    "views": row.metric_values[0].value
                } for row in pages_leading_to.rows[:self.top_n]
            ] if pages_leading_to.rows else [],
            "pages_visited_next": [
                {
                    "page": row.dimension_values[0].value,
                    "views": row.metric_values[0].value
                } for row in pages_visited_next.rows[:self.top_n]
            ] if pages_visited_next.rows else []
        }