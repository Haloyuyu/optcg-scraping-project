from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Function to initialize the driver and open the webpage
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
# driver.set_window_size(1920, 1080)
driver.get("https://en.onepiece-cardgame.com/cardlist/")

driver.find_element(By.ID, "onetrust-accept-btn-handler").click() # Accept cookies
#-------------------------------------------------------------------------------

# Function to get all sets
setList = []
setElements = []

try:
    # set_filter_bar = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, "//*[@id=\"frmSearch\"]/div[1]/div[2]/button")))
    set_filter_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "selModalButton")))
    set_filter_bar.click()
    set_list = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id=\"cardlist\"]/div[2]/div[2]")))
    set_elements = set_list.find_elements(By.CLASS_NAME, "selModalClose")
    
except Exception as e:
    assert False, f"An error occurred: {e}"

print(f"List of sets found: {[set_el.text for set_el in set_elements]}")
#-------------------------------------------------------------------------------

# Function to get all cards from each set
all_cards = []

# Loop through each set and get the cards
for idx, set_el in enumerate(set_elements): # setElements[3:-1] <------- limiting to 1 set for testing
    # Open filter if not the first iteration
    if idx > 0:
        set_filter_bar = driver.find_element(By.XPATH, "//*[@id=\"frmSearch\"]/div[1]/div[2]/button")
        set_filter_bar.click()
        set_list = driver.find_element(By.XPATH, "//*[@id=\"cardlist\"]/div[2]/div[2]")
        set_elements = set_list.find_elements(By.CLASS_NAME, "selModalClose")
        set_el = set_elements[idx]

    # Select the set 
    # set_name = set_el.text
    set_el.click()
    search_bar = driver.find_element(By.XPATH, "//*[@id=\"frmSearch\"]/div[4]/input")
    search_bar.click()
    time.sleep(2)  # Wait for the cards to load

    # Get all cards in the set
    cards = driver.find_elements(By.CLASS_NAME, "lazy")
    for idx, card in enumerate(cards[:2]): # <------- limiting to first card for testing
        try:
            card.click() # Open card modal

            # Function to retrieve card details
            # Function to retrieve card ID
            modal = driver.find_element(By.CLASS_NAME, "modalCol")
            card_id = modal.get_attribute("id")
            print(f"Card ID: {card_id}")
            #-------------------------------------------------------------------------------
            # # Function to retrieve card ID
            # data_src = card.get_attribute("data-src")
            # if data_src:
            #     m = re.search(r'card/([^/]+?)\.png', data_src, flag=re.I)
            #     card_id = m.group(1) if m else "Unknown"
            # else:
            #     card_id = "Unknown"
            # #-------------------------------------------------------------------------------
            name = card.find_element(By.CLASS_NAME, "cardName").text
            print(f"Card Name: {name}")

            cost_div = card.find_element(By.CLASS_NAME, "cost")
            if cost_div.find_elements(By.TAG_NAME, "h3").text == "Life":
                life = cost_div.text
                cost = "None"
            elif cost_div.find_elements(By.TAG_NAME, "h3").text == "Cost":
                life = "None"
                cost = cost_div.text
            else:
                life = "None"
                cost = "0"
            print(f"Cost: {cost}, Life: {life}")

            attribute_div = card.find_element(By.CLASS_NAME, "attribute")
            attribute = attribute_div.find_element(By.TAG_NAME, "i").text if attribute_div else "Unknown"
            print(f"Attribute: {attribute}")
            
            power_div = card.find_element(By.CLASS_NAME, "power")
            power = power_div.text if power_div else "0"
            print(f"Power: {power}")
            
            counter_div = card.find_element(By.CLASS_NAME, "counter")
            counter = counter_div.text if counter_div else "None"
            print(f"Counter: {counter}")

            color_div = card.find_element(By.CLASS_NAME, "color")
            color = color_div.text if color_div else "None"
            print(f"Color: {color}")

            block_div = card.find_element(By.CLASS_NAME, "block")
            block = block_div.text if block_div else "None"
            print(f"Block: {block}")

            type_div = card.find_element(By.CLASS_NAME, "feature")
            type_ = type_div.text if type_div else "None"
            print(f"Type: {type_}")

            effect_div = driver.find_element(By.CLASS_NAME, "text")
            effect = effect_div.text if effect_div else "None"
            print(f"Effect: {effect}")

            info_col = driver.find_element(By.CLASS_NAME, "infoCol")
            print(f"Additional Info: {info_col.text}")


            all_cards.append(
                {
                    "card_id": card_id,
                    "name": name
                }
            )
            #-------------------------------------------------------------------------------

            close_button = driver.find_element(By.XPATH, "//*[@id=\"fancybox-container-3\"]/div[2]/div[2]/button/svg")
            close_button.click() # Close card modal

        except Exception as e:
            print(f"Error retrieving a card: {e}")
#-------------------------------------------------------------------------------

