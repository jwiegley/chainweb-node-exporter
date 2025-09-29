#!/usr/bin/env python3
"""
Prometheus exporter for Kadena blockchain cut height.
"""

import time
import requests
import logging
from prometheus_client import start_http_server, Gauge, Counter
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Prometheus metrics
cut_height_gauge = Gauge('kadena_cut_height', 'Current cut height of the Kadena blockchain')
api_errors_counter = Counter('kadena_api_errors_total', 'Total number of API errors')
api_requests_counter = Counter('kadena_api_requests_total', 'Total number of API requests made')

class KadenaExporter:
    def __init__(self, api_url, timeout=1):
        self.api_url = api_url
        self.timeout = timeout

    def fetch_cut_height(self):
        """Fetch the current cut height from the Kadena API."""
        try:
            api_requests_counter.inc()
            response = requests.get(
                self.api_url,
                timeout=self.timeout,
                verify=False  # Equivalent to curl's -k flag
            )
            response.raise_for_status()
            data = response.json()
            height = data.get('height')

            if height is not None:
                logger.info(f"Successfully fetched cut height: {height}")
                return height
            else:
                logger.error("Height field not found in API response")
                api_errors_counter.inc()
                return None

        except requests.RequestException as e:
            logger.error(f"Error fetching data from API: {e}")
            api_errors_counter.inc()
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing API response: {e}")
            api_errors_counter.inc()
            return None

    def update_metrics(self):
        """Update Prometheus metrics with the latest cut height."""
        height = self.fetch_cut_height()
        if height is not None:
            cut_height_gauge.set(height)

    def run(self, scrape_interval=15):
        """Run the exporter loop."""
        logger.info(f"Starting Kadena exporter, scraping every {scrape_interval} seconds")

        while True:
            self.update_metrics()
            time.sleep(scrape_interval)

def main():
    parser = argparse.ArgumentParser(description='Kadena blockchain Prometheus exporter')
    parser.add_argument(
        '--port',
        type=int,
        default=9100,
        help='Port to expose metrics on (default: 9100)'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='https://api.chainweb.com/chainweb/0.0/mainnet01/cut',
        help='Kadena API URL (default: https://api.chainweb.com/chainweb/0.0/mainnet01/cut)'
    )
    parser.add_argument(
        '--scrape-interval',
        type=int,
        default=15,
        help='Interval between API calls in seconds (default: 15)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=1,
        help='API request timeout in seconds (default: 1)'
    )

    args = parser.parse_args()

    # Disable SSL warnings since we're using verify=False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Start the Prometheus metrics server
    start_http_server(args.port)
    logger.info(f"Prometheus metrics server started on port {args.port}")

    # Create and run the exporter
    exporter = KadenaExporter(args.api_url, args.timeout)
    exporter.run(args.scrape_interval)

if __name__ == '__main__':
    main()