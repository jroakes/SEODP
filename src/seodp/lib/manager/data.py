"""Data manager module for SEO Data Platform."""

from datetime import datetime, timedelta, date
from typing import Dict, Any, List, NamedTuple
import sqlite3
import json
from lib.api.gemini import GeminiAPIClient
from lib.extractors import ExtractorTools
from lib.logging import logger

class Period(NamedTuple):
    year: int
    period: int
    start: str
    end: str

class DataManager:
    def __init__(self, config: Dict):
        self.config = config
        self.db_file = config.db_file
        self.conn = sqlite3.connect(self.db_file)
        self.gemini_client = GeminiAPIClient(config)
        self.extractor_tools = ExtractorTools(config)
        self.setup_database()

    def setup_database(self) -> None:
        self.conn.execute('''CREATE TABLE IF NOT EXISTS data
                         (url TEXT, year INTEGER, period INTEGER, start_date TEXT, end_date TEXT, data TEXT, insights TEXT)''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS excluded_urls
                         (url TEXT, exclusion_date TEXT, reason TEXT)''')

    def get_current_period(self) -> Period:
        today = date.today()
        if self.config.schedule == 'monthly':
            current_month = today.replace(day=1) - timedelta(days=1)
            year = current_month.year
            period = current_month.month
            start = date(year, period, 1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:  # weekly
            current_week = today - timedelta(days=today.weekday() + 1)
            start = current_week - timedelta(days=6)
            end = current_week
            year, week, _ = end.isocalendar()
            period = week
        
        return Period(year=year, period=period,
                      start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))

    def get_prior_period(self) -> Period:
        current = self.get_current_period()
        if self.config.schedule == 'monthly':
            if current.period == 1:
                year = current.year - 1
                period = 12
            else:
                year = current.year
                period = current.period - 1
            start = date(year, period, 1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:  # weekly
            start = datetime.strptime(current.start, '%Y-%m-%d').date() - timedelta(days=7)
            end = start + timedelta(days=6)
            year, week, _ = end.isocalendar()
            period = week
        
        return Period(year=year, period=period,
                      start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))

    def get_current_data_db(self, url: str) -> Dict[str, Any]:
        current_period = self.get_current_period()
        return self._get_data(url, current_period.year, current_period.period)

    def get_prior_data_db(self, url: str) -> Dict[str, Any]:
        prior_period = self.get_prior_period()
        return self._get_data(url, prior_period.year, prior_period.period)

    def get_current_data_live(self, url: str) -> Dict[str, Any]:
        current_period = self.get_current_period()
        return self._extract_data(url, current_period)

    def get_prior_data_live(self, url: str) -> Dict[str, Any]:
        prior_period = self.get_prior_period()
        return self._extract_data(url, prior_period)

    def _get_data(self, url: str, year: int, period: int) -> Dict[str, Any]:
        c = self.conn.execute("SELECT data FROM data WHERE url=? AND year=? AND period=?", (url, year, period))
        data = c.fetchone()
        return json.loads(data[0]) if data else {}

    def _extract_data(self, url: str, period: Period) -> Dict[str, Any]:
        data = self.extractor_tools.extract_data(url, period.start, period.end)
        return {'data_attribution': {'url': url, 'date_range': f"{period.start} to {period.end}"}, 'data': data}

    def store_data(self, url: str, period: Period, data: Dict[str, Any], insights: Dict[str, Any]) -> None:
        data_json = json.dumps(data)
        insights_json = json.dumps(insights)
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO data (url, year, period, start_date, end_date, data, insights) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (url, period.year, period.period, period.start, period.end, data_json, insights_json))

    def get_all_insights(self, year: int, period: int) -> List[Dict[str, Any]]:
        c = self.conn.execute("SELECT url, insights FROM data WHERE year=? AND period=?", (year, period))
        results = c.fetchall()
        return [{"url": row[0], **json.loads(row[1])} for row in results]

    def is_url_excluded_from_processing(self, url: str) -> bool:
        c = self.conn.execute("SELECT 1 FROM excluded_urls WHERE url=?", (url,))
        result = c.fetchone()
        return bool(result)

    def exclude_low_traffic_urls_from_processing(self, urls: List[str]) -> None:
        current_period = self.get_current_period()
        low_traffic_threshold = self.config.low_traffic_threshold

        for url in urls:
            c = self.conn.execute("SELECT data FROM data WHERE url=? AND year=? AND period=?", (url, current_period.year, current_period.period))
            latest_data = c.fetchone()
            if latest_data:
                data = json.loads(latest_data[0])
                if data.get('GA4Extractor', {}).get('organic_sessions', 0) < low_traffic_threshold:
                    logger.info(f"Excluding {url} due to low traffic")
                    self._add_url_to_excluded_list(url, "Low traffic")

    def _add_url_to_excluded_list(self, url: str, reason: str) -> None:
        exclusion_date = datetime.now().strftime('%Y-%m-%d')
        with self.conn:
            self.conn.execute("INSERT INTO excluded_urls (url, exclusion_date, reason) VALUES (?, ?, ?)", (url, exclusion_date, reason))