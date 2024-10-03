import requests
from lib.extractors.base import DataExtractor

class PSIExtractor(DataExtractor):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.api_key = config.api['scrapingbee_api_key']

    def authenticate(self):
        """No authentication required for this extractor."""
        self.is_authenticated = True

    def extract_data(self, url):
        self.check_authentication()

        desktop_data = self._fetch_data(url, "DESKTOP")
        mobile_data = self._fetch_data(url, "MOBILE")

        return {
            "desktop": desktop_data,
            "mobile": mobile_data
        }

    def _fetch_data(self, url, strategy):
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            lighthouse_result = data.get("lighthouseResult", {})
            audits = lighthouse_result.get("audits", {})

            return {
                "largest_contentful_paint": audits.get("largest-contentful-paint", {}).get("numericValue"),
                "cumulative_layout_shift": audits.get("cumulative-layout-shift", {}).get("numericValue"),
                "interaction_to_next_paint": audits.get("interactive", {}).get("numericValue"),  # Using TTI as a proxy for INP
                "first_contentful_paint": audits.get("first-contentful-paint", {}).get("numericValue"),
                "time_to_interactive": audits.get("interactive", {}).get("numericValue"),
                "speed_index": audits.get("speed-index", {}).get("numericValue"),
                "total_blocking_time": audits.get("total-blocking-time", {}).get("numericValue"),
                "performance_score": lighthouse_result.get("categories", {}).get("performance", {}).get("score"),
                "first_meaningful_paint": audits.get("first-meaningful-paint", {}).get("numericValue"),
            }

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {key: None for key in ["largest_contentful_paint", "cumulative_layout_shift", "interaction_to_next_paint", 
                                          "first_contentful_paint", "time_to_interactive", "speed_index", 
                                          "total_blocking_time", "performance_score", "first_meaningful_paint"]}