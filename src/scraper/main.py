from scraper import Scraper

def main():
    scraper = Scraper()

    driver = Scraper().open_browser()
    setElements = Scraper().get_setlist(driver)
    Scraper().get_all_cards(driver, setElements)

if __name__ == "__main__":
    main()