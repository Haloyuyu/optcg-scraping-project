from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class Scraper(object):

    def __init__(self):
        pass
    
    def open_browser(self): 
        '''
        Open Chrome browser and accept cookies
        '''
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.set_window_size(1920, 1080)
        self.driver.get("https://en.onepiece-cardgame.com/cardlist/")

        self.driver.find_element(By.ID, "onetrust-accept-btn-handler").click() # Accept cookies
        return self.driver

    def get_setlist(self, driver):
        '''
        Get all sets and cards from the website
        '''
        self.setList = []
        self.setElements = []

        # Extract the set list
        try:
            self.set_filter_bar = driver.find_element(By.XPATH, "//*[@id=\"frmSearch\"]/div[1]/div[2]/button")
            self.set_filter_bar.click()
            self.set_list = driver.find_element(By.XPATH, "//*[@id=\"cardlist\"]/div[2]/div[2]")
            self.setElements = self.set_list.find_elements(By.CLASS_NAME, "selModalClose")

        except Exception as e:
            assert False, f"An error occurred: {e}"

        return self.setElements

    def get_all_cards(self, driver, setElements):
        '''
        Get all cards from all sets
        '''
        self.all_cards = []

        # Loop through each set and get the cards
        for idx, set_el in enumerate(setElements):
            # Open filter if not the first iteration
            if idx > 0:
                setElements = Scraper.get_setlist(driver)
                set_el = setElements[idx]

            # Select the set
            set_name = set_el.text
            set_el.click()
            time.sleep(2)  # Wait for the cards to load

            # Get all cards in the set
            self.cards = driver.find_elements(By.CLASS_NAME, "cardlistItem")
            for card in self.cards:
                try:
                    name = card.find_element(By.CLASS_NAME, "cardName").text
                    self.all_cards.append(
                        {
                            "set": set_name,
                            "name": name
                        }
                    )
                except Exception as e:
                    print(f"Erreur lors de la récupération d'une carte: {e}")


