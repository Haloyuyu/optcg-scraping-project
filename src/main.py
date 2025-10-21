from scraper.scraper import scrape_all_sets
from scraper.utils import export_json, export_csv

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Scrape ONE PIECE cards from ALL sets (OPTIMIZED)")
    parser.add_argument("--output", required=True, help="Output file (JSON or CSV)")
    parser.add_argument("--url", default="https://en.onepiece-cardgame.com/cardlist/")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--headful", action="store_true", help="Disable headless mode")
    parser.add_argument("--limit", type=int, help="Max cards to scrape")
    parser.add_argument("--debug", action="store_true")
    
    args = parser.parse_args()
    
    # Validate output format BEFORE scraping
    output = args.output.lower()
    if not (output.endswith('.json') or output.endswith('.csv')):
        logger.error("Output must be .json or .csv")
        sys.exit(1)
    
    headless = not args.headful
    
    cards = scrape_all_sets(
        url=args.url,
        headless=headless,
        limit=args.limit,
        debug=args.debug,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
