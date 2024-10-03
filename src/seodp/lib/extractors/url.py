""" Extract SEO content and metadata from a given URL using ScrapingBee API. """

import json
import logging
from typing import Dict, Union, List
from bs4 import BeautifulSoup

from scrapingbee import ScrapingBeeClient
from trafilatura import extract

from lib.extractors.base import DataExtractor
from lib.errors import AuthenticationError

logger = logging.getLogger(__name__)

class SEOContentExtractor(DataExtractor):
    READABILITY_JS = """
    (async function main () {
      let page_content = async()=>{
        const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
        let documentClone = document.cloneNode(true);
        let rd = new readability.Readability(documentClone)
        rd._clean_b = rd._clean
        rd._clean = function(e, tag) {
            let allowed = ['button', 'a']
            return allowed.indexOf(tag) ? this._clean_b(e, tag) > -1 : true;
        }
        let rd_result = rd.parse();
        return rd_result.content;
      }
      let content = await page_content();
      return content;
    })();
    """

    HEADERS = {
        "DNT": "1",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.api_key = config.api['scrapingbee_api_key']
        self.client = None

    def authenticate(self):
        """Authenticate with ScrapingBee API."""
        try:
            self.client = ScrapingBeeClient(api_key=self.api_key)
            # We could potentially make a test request here to verify the API key
            self.is_authenticated = True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationError("Failed to authenticate with ScrapingBee API")

    def extract_data(self, url: str) -> Dict[str, Union[str, None]]:
        """Extract SEO content and metadata from a given URL."""
        self.check_authentication()

        response = self.client.get(
            url,
            headers=self.HEADERS,
            params={
                "block_ads": "True",
                "json_response": "True",
                "wait_browser": "load",
                "js_scenario": {
                    "strict": False,
                    "instructions": [{"evaluate": self.READABILITY_JS}],
                },
            },
        )

        if response.status_code == 200:
            url_data = response.json()
            clean_content = self._extract_clean_content(url_data)
            raw_html = self._extract_raw_html(url_data)
            metadata = self._extract_metadata(raw_html)
            
            return {
                "clean_content": clean_content,
                "metadata": metadata,
                "word_count": self._get_word_count(clean_content),
                "heading_structure": self._get_heading_structure(raw_html),
                "images": self._get_images(raw_html),
                "schema_markup": self._get_schema_markup(raw_html)
            }
        
        logger.error(f"ScrapingBee error: {response.status_code}")
        return {
            "clean_content": None,
            "metadata": None,
            "word_count": None,
            "heading_structure": None,
            "images": None,
            "schema_markup": None
        }

    def _extract_clean_content(self, url_data: Dict) -> Union[str, None]:
        """Extract clean content from ScrapingBee response."""
        if isinstance(url_data, dict) and "evaluate_results" in url_data:
            content = url_data["evaluate_results"]
            if isinstance(content, list) and len(content) > 0:
                return self._format_content(content[0])
        if isinstance(url_data, dict) and "js_scenario_report" in url_data:
            report = url_data["js_scenario_report"]
            logger.error(f"ScrapingBee error: {json.dumps(report, indent=2)}")
        return None

    def _extract_raw_html(self, url_data: Dict) -> Union[str, None]:
        """Extract raw HTML from ScrapingBee response."""
        if isinstance(url_data, dict) and "body" in url_data:
            return url_data["body"]
        return None

    def _extract_metadata(self, raw_html: str) -> Union[Dict, None]:
        """Extract metadata using Trafilatura."""
        if raw_html:
            metadata = extract(raw_html, output_format="json", include_comments=False, with_metadata=True)
            return json.loads(metadata) if metadata else None
        return None

    @staticmethod
    def _format_content(content: str) -> str:
        """Format the extracted content to clean text. Removing any HTML, Scripts, 
        non-alphanumeric characters, execcesive whitespaces, etc."""

        # Remove HTML tags
        content = BeautifulSoup(content, 'html.parser').get_text()

        # Remove non-alphanumeric characters
        content = ''.join(e for e in content if e.isalnum() or e.isspace())

        # Remove excessive whitespaces
        content = ' '.join(content.split())

        return content

    def _get_word_count(self, content: str) -> int:
        """Get word count from clean content."""
        return len(content.split())

    def _get_heading_structure(self, raw_html: str) -> Dict[str, int]:
        """Get heading structure from raw HTML."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        headings = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings[tag.name] += 1
        return headings

    def _get_images(self, raw_html: str) -> List[Dict[str, str]]:
        """Get images from raw HTML."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', '')
            })
        return images

    def _get_schema_markup(self, raw_html: str) -> List[Dict]:
        """Get schema markup from raw HTML."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        schema_tags = soup.find_all('script', type='application/ld+json')
        schema_data = []
        for tag in schema_tags:
            try:
                schema_data.append(json.loads(tag.string))
            except:
                pass
        return schema_data