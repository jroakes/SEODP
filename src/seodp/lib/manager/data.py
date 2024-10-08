"""Data processing module for SEO Data Platform."""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, NamedTuple
from settings import CONFIG
from lib.api.gemini import GeminiAPIClient
from lib.extractors import ExtractorTools
from lib.logging import logger

class Period(NamedTuple):
    start: str
    end: str

class DataManager:
    def __init__(self, config: Dict):
        self.config = config
        self.db_file = config.db_file
        self.gemini_client = GeminiAPIClient(config)
        self.extractor_tools = ExtractorTools(config)
        self.setup_database()

    @property
    def t_period_days(self):
        return 30 if self.config.schedule == 'monthly' else 7

    def get_current_period(self) -> Period:
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=self.t_period_days)
        return Period(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    def get_prior_period(self) -> Period:
        current_period = self.get_current_period()
        start_date = datetime.strptime(current_period.start, '%Y-%m-%d') - timedelta(days=self.t_period_days)
        end_date = datetime.strptime(current_period.start, '%Y-%m-%d') - timedelta(days=1)
        return Period(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    def setup_database(self) -> None:
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS data
                         (url TEXT, run_date TEXT, data TEXT, insights TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS excluded_urls
                         (url TEXT, exclusion_date TEXT, reason TEXT)''')

    def extract_data(self, url: str, period: Period) -> Dict[str, Any]:
        return self.extractor_tools.extract_data(url, period.start, period.end)

    def get_prior_data(self, url: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT data FROM data WHERE url=? ORDER BY run_date DESC LIMIT 1", (url,))
            prior_data = c.fetchone()
        return json.loads(prior_data[0]) if prior_data else {}

    def store_data(self, url: str, run_date: str, data: Dict[str, Any], insights: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            data_json = json.dumps(data)
            insights_json = json.dumps(insights)
            c.execute("INSERT INTO data (url, run_date, data, insights) VALUES (?, ?, ?, ?)", 
                      (url, run_date, data_json, insights_json))

    def get_all_insights(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT url, insights FROM data WHERE run_date BETWEEN ? AND ?", (start_date, end_date))
            results = c.fetchall()
        return [{"url": row[0], **json.loads(row[1])} for row in results]

    def is_url_excluded_from_processing(self, url: str) -> bool:
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT 1 FROM excluded_urls WHERE url=?", (url,))
            result = c.fetchone()
        return bool(result)

    def exclude_low_traffic_urls_from_processing(self, urls: List[str]) -> None:
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            low_traffic_threshold = self.config.low_traffic_threshold

            for url in urls:
                c.execute("SELECT data FROM data WHERE url=? ORDER BY run_date DESC LIMIT 1", (url,))
                latest_data = c.fetchone()
                if latest_data:
                    data = json.loads(latest_data[0])
                    if data.get('Google Analytics', {}).get('sessions', 0) < low_traffic_threshold:
                        logger.info(f"Excluding {url} due to low traffic")
                        self.add_url_to_excluded_list(url, "Low traffic")

    def add_url_to_excluded_list(self, url: str, reason: str) -> None:
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            exclusion_date = datetime.now().strftime('%Y-%m-%d')
            c.execute("INSERT INTO excluded_urls (url, exclusion_date, reason) VALUES (?, ?, ?)", (url, exclusion_date, reason))

    def get_last_processing_date(self) -> datetime:
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT MAX(run_date) FROM data")
            last_run_date = c.fetchone()[0]
        return datetime.strptime(last_run_date, '%Y-%m-%d') if last_run_date else None

    def get_current_data_db(self, url: str) -> Dict[str, Any]:
        period = self.get_current_period()
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT data FROM data WHERE url=? AND run_date BETWEEN ? AND ? ORDER BY run_date DESC LIMIT 1", 
                      (url, period.start, period.end))
            data = c.fetchone()
        return json.loads(data[0]) if data else {}

    def get_prior_data_db(self, url: str) -> Dict[str, Any]:
        period = self.get_prior_period()
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT data FROM data WHERE url=? AND run_date BETWEEN ? AND ? ORDER BY run_date DESC LIMIT 1", 
                      (url, period.start, period.end))
            data = c.fetchone()
        return json.loads(data[0]) if data else {}

    def get_current_data_live(self, url: str) -> Dict[str, Any]:
        period = self.get_current_period()
        return self.extract_data(url, period)

    def get_prior_data_live(self, url: str) -> Dict[str, Any]:
        period = self.get_prior_period()
        return self.extract_data(url, period)