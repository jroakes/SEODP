import sqlite3
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from settings import CONFIG
from lib.api.gemini import GeminiAPIClient
from lib.extractors import ExtractorTools


class URLProcessor:
    def __init__(self, config):
        self.config = config
        self.db_file = config.db_file
        self.schedule = config.schedule
        self.process_interval = timedelta(weeks=1) if self.schedule == 'weekly' else timedelta(days=30)
        self.last_run = self.get_last_run_date()
        self.next_run = self.last_run + self.process_interval if self.last_run else datetime.now()
        self.data_processor = DataProcessor(config)

    def get_last_run_date(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT MAX(run_date) FROM data")
        last_run_date = c.fetchone()[0]
        conn.close()
        return datetime.strptime(last_run_date, '%Y-%m-%d') if last_run_date else None

    def run(self):
        while self.next_run <= datetime.now():
            run_date = self.next_run.strftime('%Y-%m-%d')
            print(f"Running URLs for {run_date}")

            urls = self.extract_urls_from_sitemap(self.config.sitemap_file)
            for url in urls:
                if not self.data_processor.is_url_excluded(url):
                    print(f"Processing {url}")
                    current_data = self.data_processor.extract_data(url)
                    prior_data = self.data_processor.get_prior_data(url, run_date)
                    analysis = self.data_processor.generate_insights(current_data, prior_data)
                    self.data_processor.store_data(url, run_date, current_data, analysis)
                else:
                    print(f"Skipping excluded URL: {url}")

            self.data_processor.exclude_low_traffic_urls(urls)
            self.next_run += self.process_interval

    def run_test(self, url):
        run_date = datetime.now().strftime('%Y-%m-%d')
        t_period_days = 30 if self.schedule == 'monthly' else 7
        current_start_date = (datetime.now() - timedelta(days=t_period_days)).strftime('%Y-%m-%d')
        prior_start_date = (datetime.now() - timedelta(days=t_period_days * 2)).strftime('%Y-%m-%d')
        current_end_date = datetime.now().strftime('%Y-%m-%d')
        prior_end_date = (datetime.now() - timedelta(days=t_period_days)).strftime('%Y-%m-%d')

        current_data = self.data_processor.extract_data(url, current_start_date, current_end_date)
        prior_data = self.data_processor.extract_data(url, prior_start_date, prior_end_date)
        analysis = self.data_processor.generate_insights(current_data, prior_data)
        return analysis

    def extract_data(self, url):
        return self.data_processor.extract_data(url)

    def extract_urls_from_sitemap(self, sitemap_file):
        urls = []
        try:
            tree = ET.parse(sitemap_file)
            root = tree.getroot()
            namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for url in root.findall('sitemap:url', namespace):
                loc = url.find('sitemap:loc', namespace)
                if loc is not None:
                    urls.append(loc.text)
        except ET.ParseError as e:
            print(f"Error parsing sitemap: {e}")
        return urls


class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.db_file = config.db_file
        self.gemini_client = GeminiAPIClient(config)
        self.extractor_tools = ExtractorTools(config)
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS data
                     (url TEXT, run_date TEXT, data TEXT, analysis TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS excluded_urls
                     (url TEXT, exclusion_date TEXT, reason TEXT)''')
        conn.commit()
        conn.close()

    def extract_data(self, url, start_date=None, end_date=None):
        return self.extractor_tools.extract_data(url, start_date, end_date)

    def get_prior_data(self, url, run_date):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT data FROM data WHERE url=? AND run_date < ? ORDER BY run_date DESC LIMIT 1", (url, run_date))
        prior_data = c.fetchone()
        conn.close()
        return json.loads(prior_data[0]) if prior_data else {}

    def generate_insights(self, current_data, prior_data):
        analysis = self.gemini_client.generate_insights(current_data, prior_data)
        return analysis

    def store_data(self, url, run_date, data, analysis):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        data_json = json.dumps(data)
        c.execute("INSERT INTO data (url, run_date, data, analysis) VALUES (?, ?, ?, ?)", (url, run_date, data_json, analysis))
        conn.commit()
        conn.close()

    def exclude_low_traffic_urls(self, urls):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        low_traffic_threshold = self.config.low_traffic_threshold

        for url in urls:
            c.execute("SELECT data FROM data WHERE url=? ORDER BY run_date DESC LIMIT 1", (url,))
            latest_data = c.fetchone()
            if latest_data:
                data = json.loads(latest_data[0])
                if data.get('ga4', {}).get('sessions', 0) < low_traffic_threshold:
                    print(f"Excluding {url} due to low traffic")
                    self.add_excluded_url(url, "Low traffic")

        conn.close()

    def add_excluded_url(self, url, reason):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        exclusion_date = datetime.now().strftime('%Y-%m-%d')
        c.execute("INSERT INTO excluded_urls (url, exclusion_date, reason) VALUES (?, ?, ?)", (url, exclusion_date, reason))
        conn.commit()
        conn.close()

    def is_url_excluded(self, url):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT 1 FROM excluded_urls WHERE url=?", (url,))
        result = c.fetchone()
        conn.close()
        return bool(result)

    def get_excluded_urls(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT url, exclusion_date, reason FROM excluded_urls")
        excluded_urls = c.fetchall()
        conn.close()
        return excluded_urls

    def remove_excluded_url(self, url):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("DELETE FROM excluded_urls WHERE url=?", (url,))
        conn.commit()
        conn.close()

    def generate_report(self, start_date, end_date):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT url, run_date, data, analysis FROM data WHERE run_date BETWEEN ? AND ? ORDER BY url, run_date", (start_date, end_date))
        report_data = c.fetchall()
        conn.close()

        # Process and format report data
        report = {"urls": {}}
        for url, run_date, data, analysis in report_data:
            if url not in report["urls"]:
                report["urls"][url] = []
            report["urls"][url].append({
                "run_date": run_date,
                "data": json.loads(data),
                "analysis": analysis
            })

        return report