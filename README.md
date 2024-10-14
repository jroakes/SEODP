# SEO Data Platform

## Description

The SEO Data Platform is a comprehensive tool designed to automate the collection, analysis, and reporting of SEO-related data. It integrates with various data sources such as Google Analytics 4, Google Search Console, and PageSpeed Insights to provide actionable insights for improving website performance and search engine rankings.

## Features

- Automated data collection from multiple sources
- Integration with Google Analytics 4, Google Search Console, and PageSpeed Insights
- URL content extraction and analysis
- LLM-powered insights generation using Google's Gemini API
- Configurable reporting topics and significance thresholds
- Scheduled data processing and report generation
- Email reporting functionality

## Installation

1. Clone the repository:
```
git clone https://github.com/jroakes/SEODP.git 
cd SEODP
```

2. Install the required dependencies:
`pip install -r requirements.txt`
You can also use poetry.

3. Set up the configuration file:
- Edit `seodpconfig.yaml` with your specific settings

4. Set up environment variables:
- Create a `.env` file in the project root
- Add the required API keys and credentials (see Configuration section)


## Usage

To start the SEO Data Platform:

`python src/seodp/main.py --start`


For other command-line options:

`python src/seodp/main.py --help`


## Configuration

### Environment Variables

Set the following environment variables in your `.env` file:

- `SERVICE_ACCOUNT_FILE_PATH`: Path to your Google service account JSON file
- `SUBJECT_EMAIL`: Email address for Google API authentication
- `SCRAPINGBEE_API_KEY`: Your ScrapingBee API key
- `GEMINI_API_KEY`: Your Google Gemini API key
- `MAILTRAP_LOGIN`: Your Mailtrap login
- `MAILTRAP_PASSWORD`: Your Mailtrap password
- `MAILTRAP_SENDER_EMAIL`: Sender email for Mailtrap
- `RECIPIENT_EMAIL`: Recipient email for reports

See `.env.example` example file.

### Configuration File

Edit `seodpconfig.yaml` to customize:

- URLs to analyze
- Reporting schedule
- Data sources and API settings
- Reporting topics and thresholds

## Project Structure

- `src/seodp/`: Main source code directory
  - `main.py`: Entry point of the application
  - `settings.py`: Configuration loading and management
  - `lib/`: Core functionality modules
    - `extractors/`: Data extraction modules for different sources
    - `manager/`: Data processing and management modules
    - `api/`: API client modules (e.g., Gemini, email)

## Contributing

Contributions to the SEO Data Platform are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your fork
5. Submit a pull request

Please ensure your code adheres to the project's coding standards and include tests for new functionality.

## License
MIT