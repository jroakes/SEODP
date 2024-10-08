# SEO Data Platform (SEODP)

This project is a Python-based SEO Data Platform designed to automate data extraction, analysis, and reporting for SEO purposes. It leverages various APIs and tools to gather data from sources like Google Search Console, Google Analytics 4, Page Speed Insights, and directly from URLs. The platform then uses a Large Language Model (LLM), specifically Google's Gemini, to generate insights and analysis based on the collected data.

## Features

* **Automated Data Extraction:** Extracts data from multiple SEO data sources.
* **LLM-Powered Insights:** Uses Gemini to generate actionable insights and analysis.
* **Scheduled Runs:** Supports scheduled data extraction and reporting.
* **Data Storage:** Stores historical data for trend analysis.
* **Customizable Reporting:** Generates reports in various formats (e.g., JSON, email).
* **Low Traffic URL Exclusion:** Automatically excludes URLs with low traffic to focus on important pages.
* **Sitemap Processing:** Extracts URLs from a sitemap for comprehensive analysis.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   ```
2. Navigate to the project directory:
   ```bash
   cd SEODP
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
5. Configure the `.env` file with your API keys and other settings.

## Usage

The platform can be run in different modes:

* **Scheduled Run:**
   ```bash
   python src/seodp/main.py --run
   ```
* **Test Mode (for a single URL):**
   ```bash
   python src/seodp/main.py --test -u <url>
   ```
* **Sitemap Test Workflow:**
   ```bash
   python src/seodp/main.py --sitemap-test
   ```
* **Analyze a Single URL:**
   ```bash
   python src/seodp/main.py -u <url>
   ```

## Configuration

The `settings.py` file contains the main configuration settings. The `.env` file should contain the following environment variables:

* `SERVICE_ACCOUNT_FILE_PATH`: Path to your Google service account credentials file.
* `SUBJECT_EMAIL`: Email address associated with your Google service account.
* `SCRAPINGBEE_API_KEY`: Your ScrapingBee API key.
* `GEMINI_API_KEY`: Your Gemini API key.
* `SENDGRID_API_KEY`: Your SendGrid API key.


## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License.