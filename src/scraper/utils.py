from scraper import Card

from typing import List
import sys
import csv
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def export_json(cards: List[Card], filepath: str):
    """Export to JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('[\n')
        for idx, card in enumerate(cards):
            json.dump(card.to_dict(), f, ensure_ascii=False)
            if idx < len(cards) - 1:
                f.write(',\n')
        f.write('\n]\n')
    logger.info(f"✓ Exported {len(cards)} cards to {filepath}")


def export_csv(cards: List[Card], filepath: str):
    """Export to CSV."""
    if not cards:
        logger.warning("No cards to export")
        return
    keys = cards[0].to_dict().keys()
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for card in cards:
            writer.writerow(card.to_dict())
    logger.info(f"✓ Exported {len(cards)} cards to {filepath}")

