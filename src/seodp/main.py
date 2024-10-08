"""Main module to handle command-line arguments and initiate the SEO Data Platform."""

import argparse
import json
from lib.manager import Manager
from settings import CONFIG
from lib.logging import logger

def main():
    """
    Main function to handle command-line arguments and initiate the SEO Data Puller.
    """
    parser = argparse.ArgumentParser(description='SEO Data Puller')
    parser.add_argument('-u', '--url', type=str, help='Page URL to analyze')
    parser.add_argument('--test', action='store_true', help='Run test mode to compare data with previous period')
    parser.add_argument('-o', '--output', type=str, help='Output file for JSON or insights')
    parser.add_argument('--run', action='store_true', help='Start the process and run the schedule')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--sitemap-test', action='store_true', help='Run sitemap test workflow')
    args = parser.parse_args()

    if args.debug:
        logger.level('DEBUG')
    else:
        logger.level('INFO')

    manager = Manager(CONFIG)

    results = None

    if args.run:
        manager.run_schedule()
    elif args.test:
        if not args.url:
            logger.error("Please provide a URL with -u/--url in test mode.")
            return
        results = manager.run_test(args.url)
        logger.info(f"Test results: {results}")
    elif args.sitemap_test:
        results = manager.run_sitemap_test()
        logger.info("Sitemap test completed")
    elif args.url:
        results = manager.run_single_url(args.url)
        logger.info(f"Single URL results: {results}")
    else:
        parser.print_help()

    if results and args.output:
        try:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=4)
            logger.info(f"Results written to {args.output}")
        except IOError as e:
            logger.error(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()