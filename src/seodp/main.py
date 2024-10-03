import argparse
import json
from lib.process import URLProcessor

from settings import CONFIG
from lib.logging import logger


def main():
    parser = argparse.ArgumentParser(description='SEO Data Puller')
    parser.add_argument('-u', '--url', type=str, help='Page URL to analyze')
    parser.add_argument('--test', action='store_true', help='Run test mode to compare data with previous period')
    parser.add_argument('-o', '--output', type=str, help='Output file for JSON or insights')
    parser.add_argument('--run', action='store_true', help='Start the process and run the schedule')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logger.level('DEBUG')
    else:
        logger.level('INFO')

    url_processor = URLProcessor(CONFIG)

    if args.run:
        url_processor.run()
    elif args.test and args.url and args.output:
        insights = url_processor.run_test(args.url)
        with open(args.output, 'w') as f:
            f.write(insights)
    elif args.url and args.output:
        page_full_url = args.url
        data = url_processor.extract_data(page_full_url)
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=4)
    elif args.url and not args.output:
        logger.warning("No output file specified, data will not be saved.")
    else:
        logger.error("Please provide either -u/--url or --run argument")


if __name__ == "__main__":
    main()