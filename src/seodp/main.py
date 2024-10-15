"""Main module to handle command-line arguments and initiate the SEO Data Platform."""

import argparse
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from lib.manager import Manager
from lib import logconfig
from settings import CONFIG
from loguru import logger


def start_scheduled_run():
    """Start the scheduled SEO data processing."""
    manager = Manager(CONFIG)
    manager.run_schedule()


def main():
    """
    Main function to handle command-line arguments and initiate the SEO Data Platform.
    """
    parser = argparse.ArgumentParser(description='SEO Data Platform')
    parser.add_argument('--start', action='store_true', help='Start the main long running process')
    parser.add_argument('--url_test', type=str, help='Test the URL and save results to file')
    parser.add_argument('-o', '--output', type=str, help='Output file for JSON or insights')
    parser.add_argument('--sitemap_test', action='store_true', help='Run the example sitemap URLs and save results to a file')
    parser.add_argument('--email_test', action='store_true', help='Run the example sitemap URLs and email the results')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logger.level('DEBUG')
    else:
        logger.level('INFO')

    manager = Manager(CONFIG)

    results = None  # Initialize results

    if args.start:
        schedule = os.getenv('SCHEDULE', 'monthly')
        if schedule not in ['weekly', 'monthly']:
            logger.error("Invalid SCHEDULE value. Must be 'weekly' or 'monthly'.")
            return

        scheduler = BlockingScheduler()
        if schedule == 'weekly':
            scheduler.add_job(start_scheduled_run, 'cron', day_of_week='mon', hour=0, minute=0)
        else:  # monthly
            scheduler.add_job(start_scheduled_run, 'cron', day=1, hour=0, minute=0)

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("SEO Data Platform stopped")
    elif args.url_test:
        results = manager.run_url_test(args.url_test)
        if results:
            logger.info(f"Test results: {results}")
        else:
            logger.error(f"Error running URL test for {args.url_test}")
    elif args.sitemap_test:
        if CONFIG.test_sitemap_urls:
            results = manager.run_sitemap_test(CONFIG.test_sitemap_urls)
            logger.info("Sitemap test completed")
        else:
            logger.error("No sitemap URLs provided for testing.")
    elif args.email_test:
        recipient_email = os.getenv('RECIPIENT_EMAIL')
        if not recipient_email:
            logger.error("RECIPIENT_EMAIL environment variable is not set.")
            return
        manager.run_email_test(recipient_email)
        logger.info("Email test completed")
    else:
        parser.print_help()

    if args.output and results is not None:  # Check if results is defined
        manager.save_results(results, args.output)

if __name__ == "__main__":
    logconfig.setup()
    main()
