# OPTCG Scraping Project

## 📜 OPTCG Scraping Tool
This project collects and processes card data from the official One Piece Card Game website. It provides a fast scraper, basic cleaning routines, and utilities to prepare the dataset for analysis or downstream apps.

## 🔍 Key Features
- Fast extraction using Selenium + BeautifulSoup to render pages and parse HTML.
- Streaming export to JSON or CSV while scraping large sets.
- Data cleaning helpers (normalizing costs, numeric conversion, etc.).

## 🛠️ Tech Stack
- Python 3.8+
- Selenium
- BeautifulSoup (bs4)
- webdriver-manager (for chromedriver)

## 📂 Project Layout (important files)
- `src/` — main application source code (primary entry points and scraper logic).
- `src/scraper/` — scraper implementation and helpers.
- `data/raw/` — raw JSON dumps created by the scraper.
- `data/processed/` — cleaned and normalized outputs.
- `data_processing/opcg_data.ipynb` — notebook for cleaning and exploration (includes cost normalization).
- `requirements.txt` — Python dependencies.

## Running the scraper
The scraper uses chromedriver, which requires a matching Chrome/Chromium browser binary to be installed or pointed to explicitly.

1. Install dependencies (recommended inside a virtualenv):

```powershell
python -m pip install -r requirements.txt
```

2. If Chrome/Chromium is installed normally, webdriver-manager will try to download a compatible chromedriver automatically. If the browser binary is not discoverable, set the `CHROME_BIN` environment variable to the full path of the browser executable (Windows example below).

```powershell
# Example: set CHROME_BIN for the current PowerShell session
$env:CHROME_BIN = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
python .\src\scraper\main.py --output card_output.json
```

If you prefer to install Chrome using Chocolatey:

```powershell
choco install googlechrome -y
```

3. Run headful (visible) browser for debugging:

```powershell
python .\src\scraper\main.py --output card_output.json --headful
```

## Driver detection improvements
- The scraper now attempts to locate the Chrome/Chromium binary via the `CHROME_BIN` environment variable and common Windows installation paths. If no browser binary is discoverable, it logs a clear message explaining how to set `CHROME_BIN` or install Chrome.

## Data cleaning note — cost normalization
In the dataset some cards use the string `"-"` to indicate no cost. The data-processing notebook includes a normalization step that:

- Replaces `'-'` (and empty strings / None) with `0` in the `cost` column.


## Contributing & Notes
- Respect the target site's terms of service and robots.txt.
- If you encounter environment/driver issues, set `CHROME_BIN` or install Chrome for your OS.

----