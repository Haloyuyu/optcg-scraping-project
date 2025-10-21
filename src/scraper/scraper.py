#!/usr/bin/env python3
"""
ONE PIECE Card Game Scraper v3 OPTIMIZED - ALL SETS
Ultra-fast version using BeautifulSoup for parsing (10x faster than v2)
"""

from __future__ import annotations
import csv
import json
import logging
import os
import shutil
import sys
import time
from typing import List, Optional
from tqdm import tqdm

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from card import Card

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def setup_driver(headless: bool = True):
    """Setup Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    # Try to locate a Chrome/Chromium binary. Selenium's chromedriver requires
    # the browser binary to be installed and discoverable; on some systems
    # (CI, portable environments) this isn't the case. Allow overriding with
    # CHROME_BIN env var and check common Windows install locations.
    chrome_bin = os.environ.get("CHROME_BIN") or os.environ.get("GOOGLE_CHROME_SHIM")
    if not chrome_bin:
        # Common locations for Chrome/Chromium on Windows
        possible = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles%\Chromium\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Chromium\Application\chrome.exe"),
        ]
        for p in possible:
            if p and os.path.exists(p):
                chrome_bin = p
                break
    if chrome_bin:
        try:
            options.binary_location = chrome_bin
            logger.info(f"✓ Using Chrome binary: {chrome_bin}")
        except Exception:
            # Don't fail here; chromedriver may still work if Chrome is on PATH
            logger.debug("Could not set options.binary_location, continuing without it")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    try:
        chromedriver_path = shutil.which("chromedriver")
        if chromedriver_path:
            logger.info(f"✓ Using local chromedriver: {chromedriver_path}")
            service = Service(chromedriver_path)
        else:
            logger.info("Downloading chromedriver...")
            driver_path = ChromeDriverManager().install()
            os.chmod(driver_path, 0o755)
            service = Service(driver_path)

        # Before creating the webdriver, if we couldn't determine a Chrome
        # binary, give a clearer error to the user rather than the generic
        # "cannot find Chrome binary" Selenium message.
        if not getattr(options, 'binary_location', None):
            # Quick PATH check for chrome/chromium executables
            if not (shutil.which('chrome') or shutil.which('chrome.exe') or shutil.which('chromium') or shutil.which('chromium.exe')):
                logger.error("Chrome/Chromium binary not found. Set CHROME_BIN env var to the browser executable or install Chrome.")
        return webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logger.error(f"Driver setup failed: {e}")
        raise


def extract_card_from_html(card_elem, debug: bool = False) -> Optional[Card]:
    """Extract card data from BeautifulSoup element (FAST)."""
    try:
        card_name = ""
        card_id = card_elem.get("id", None)
        
        # Get card name - it's a div with class cardName inside dt
        dt = card_elem.find("dt")
        if dt:
            card_name_elem = dt.find("div", class_="cardName")
            if card_name_elem:
                card_name = card_name_elem.get_text(strip=True)
                # Clean up multiple spaces
                card_name = " ".join(card_name.split())
        
        if not card_name or len(card_name.strip()) < 2:
            return None
        
        # Get rarity and card type from infoCol spans (inside dt)
        rarity = None
        card_type = None
        if dt:
            info_col = dt.find("div", class_="infoCol")
            if info_col:
                spans = info_col.find_all("span")
                if len(spans) >= 2:
                    rarity = spans[1].get_text(strip=True)
                if len(spans) >= 3:
                    card_type = spans[2].get_text(strip=True)
        
        # Get image URL (in frontCol inside dd)
        image_url = None
        dd = card_elem.find("dd")
        if dd:
            img = dd.find("img", class_="lazy")
            if img:
                data_src = img.get("data-src") or img.get("src")
                if data_src:
                    if data_src.startswith("../"):
                        image_url = "https://en.onepiece-cardgame.com/images/cardlist/card/" + data_src.replace("../images/cardlist/card/", "")
                    elif data_src.startswith("/"):
                        image_url = "https://en.onepiece-cardgame.com" + data_src
                    elif not data_src.startswith("http"):
                        image_url = "https://en.onepiece-cardgame.com/" + data_src
                    else:
                        image_url = data_src
        
        # Get metadata from backCol (in dd)
        cost = None
        life = None
        power = None
        attribute = None
        counter = None
        block = None
        color = None
        effect = None
        feature = None
        set_name = None
        
        if dd:
            back_col = dd.find("div", class_="backCol")
            if back_col:
                # Cost (or Life for LEADER cards)
                cost_elem = back_col.find("div", class_="cost")
                if cost_elem:
                    cost_text = cost_elem.get_text(strip=True)
                    if cost_text:
                        value = cost_text.replace("Cost", "").replace("Life", "").strip()
                        if card_type == "LEADER" and value:
                            life = value
                        elif value:
                            cost = value
                
                # Power
                power_elem = back_col.find("div", class_="power")
                if power_elem:
                    power_text = power_elem.get_text(strip=True)
                    if power_text:
                        power = power_text.replace("Power", "").strip()
                
                # Attribute
                attr_elem = back_col.find("div", class_="attribute")
                if attr_elem:
                    attr_text = attr_elem.get_text(strip=True)
                    if attr_text:
                        attribute = attr_text.replace("Attribute", "").strip()
                        # Clean up multiple spaces
                        attribute = " ".join(attribute.split())
                
                # Counter
                counter_elem = back_col.find("div", class_="counter")
                if counter_elem:
                    counter_text = counter_elem.get_text(strip=True)
                    if counter_text:
                        counter = counter_text.replace("Counter", "").strip()
                
                # Block
                block_elem = back_col.find("div", class_="block")
                if block_elem:
                    block_text = block_elem.get_text(strip=True)
                    if block_text:
                        block = block_text.replace("Block", "").replace("icon", "").strip()
                
                # Color
                color_elem = back_col.find("div", class_="color")
                if color_elem:
                    color_text = color_elem.get_text(strip=True)
                    if color_text:
                        color = color_text.replace("Color", "").strip()
                
                # Effect
                effect_elem = back_col.find("div", class_="text")
                if effect_elem:
                    effect_text = effect_elem.get_text(strip=True)
                    if effect_text:
                        effect = effect_text.replace("Effect", "").strip()
                        # Clean up multiple spaces but preserve single spaces
                        effect = " ".join(effect.split())
                        # Fix cases where space before "attribute" was lost
                        effect = effect.replace("your attribute", "your attribute").replace("byattribute", "by attribute").replace("yourattribute", "your attribute")
                
                # Feature
                feature_elem = back_col.find("div", class_="feature")
                if feature_elem:
                    feature_text = feature_elem.get_text(strip=True)
                    if feature_text:
                        feature = feature_text.replace("Type", "").strip()
                
                # Set name
                getinfo_elem = back_col.find("div", class_="getInfo")
                if getinfo_elem:
                    getinfo_text = getinfo_elem.get_text(strip=True)
                    if getinfo_text:
                        set_name = getinfo_text.replace("Card Set(s)", "").strip()
        
        return Card(
            card_name=card_name.strip(),
            card_id=card_id,
            set_name=set_name,
            rarity=rarity,
            card_type=card_type,
            cost=cost,
            life=life,
            power=power,
            image_url=image_url,
            attribute=attribute,
            counter=counter,
            block=block,
            color=color,
            effect=effect,
            feature=feature,
        )

    except Exception as e:
        if debug:
            logger.debug(f"HTML extract error: {type(e).__name__}: {str(e)[:100]}")
        return None


def get_available_sets(driver, debug: bool = False) -> List[tuple]:
    """Get all available sets from dropdown."""
    sets = []
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "series"))
        )
        
        series_select = driver.find_element(By.ID, "series")
        options = series_select.find_elements(By.TAG_NAME, "option")
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if not text:
                text = opt.get_attribute("textContent").strip()
            
            text = text.replace('<br class="spInline">', ' ').replace('<br>', ' ').strip()
            
            if value and text and text.lower() not in ["recording", ""]:
                sets.append((value, text))
                if debug:
                    logger.info(f"  Found set: {text} (id={value})")
    except Exception as e:
        logger.warning(f"Could not get sets: {e}")
    return sets


def select_set(driver, base_url: str, set_id: str) -> bool:
    """Navigate to set and wait for cards to load."""
    try:
        url_with_series = f"{base_url}?series={set_id}"
        driver.get(url_with_series)
        WebDriverWait(driver, 10, poll_frequency=0.1).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "dl.modalCol"))
        )
        return True
    except Exception as e:
        logger.warning(f"Could not select set: {e}")
        return False


def scrape_all_sets(
    url: str = "https://en.onepiece-cardgame.com/cardlist/",
    headless: bool = True,
    limit: Optional[int] = None,
    debug: bool = False,
    output_file: Optional[str] = None,
) -> List[Card]:
    """Scrape ALL sets using BeautifulSoup (FAST). Optionally stream to file."""
    driver = None
    cards = []
    seen_keys = set()
    start_time = time.time()
    output_handle = None
    is_json = output_file and output_file.lower().endswith('.json')
    is_csv = output_file and output_file.lower().endswith('.csv')
    csv_writer = None
    first_card = True

    try:
        # Open output file if streaming
        if output_file:
            output_handle = open(output_file, 'w', encoding='utf-8', newline='' if is_csv else '')
            if is_json:
                output_handle.write('[\n')
            elif is_csv:
                # Will write CSV header on first card
                pass

        driver = setup_driver(headless)
        driver.set_window_size(1280, 720)
        logger.info(f"Opening {url}")
        driver.get(url)
        time.sleep(0.5)
        
        # Get all sets
        logger.info("Fetching available sets...")
        all_sets = get_available_sets(driver, debug=debug)
        logger.info(f"✓ Found {len(all_sets)} sets")

        driver.get(url)

        # Loop through each set with progress bar
        for set_idx, (set_id, set_name) in enumerate(tqdm(all_sets, desc="Sets", unit="set", ncols=80, leave=True, file=sys.stderr), 1):
            set_start = time.time()
            
            if not select_set(driver, url, set_id):
                continue
            
            time.sleep(0.1)
            
            # Get full page HTML via JavaScript (after rendering is complete)
            try:
                page_html = driver.execute_script("return document.documentElement.outerHTML;")
            except Exception as e:
                continue
            
            # Parse with BeautifulSoup (FAST)
            soup = BeautifulSoup(page_html, "html.parser")
            card_elements = soup.find_all("dl", class_="modalCol")
            
            if not card_elements:
                continue
            
            # Extract all cards from HTML (no more Selenium!)
            set_new = 0
            extraction_errors = 0
            for elem in card_elements:
                try:
                    card = extract_card_from_html(elem, debug=debug)
                    if card is None:
                        extraction_errors += 1
                        continue
                    
                    key = card.card_id if card.card_id else card.card_name
                    
                    if key not in seen_keys:
                        cards.append(card)
                        seen_keys.add(key)
                        set_new += 1
                        
                        # Stream to file immediately
                        if output_handle:
                            if is_json:
                                if not first_card:
                                    output_handle.write(',\n')
                                json.dump(card.to_dict(), output_handle, ensure_ascii=False)
                                first_card = False
                            elif is_csv:
                                if first_card:
                                    csv_writer = csv.DictWriter(output_handle, fieldnames=card.to_dict().keys())
                                    csv_writer.writeheader()
                                    first_card = False
                                csv_writer.writerow(card.to_dict())
                            output_handle.flush()
                        
                        if limit and len(cards) >= limit:
                            logger.info(f"Reached limit: {limit}")
                            if output_handle and is_json:
                                output_handle.write('\n]\n')
                            return cards
                
                except Exception as e:
                    extraction_errors += 1
                    if debug and extraction_errors <= 3:
                        logger.debug(f"Extraction exception: {type(e).__name__}: {e}")
                    continue
            
            if limit and len(cards) >= limit:
                break
        
        # Close JSON array
        if output_handle and is_json:
            output_handle.write('\n]\n')
        
        total_time = time.time() - start_time
        logger.info(f"✓ Done in {total_time:.1f}s - {len(cards)} cards")

    finally:
        if output_handle:
            output_handle.close()
        if driver:
            driver.quit()

    return cards
