from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)
driver.get("https://en.onepiece-cardgame.com/cardlist/")

driver.find_element(By.ID, "onetrust-accept-btn-handler").click() # Accept cookies


# Get the setlist
setList = []
setElements = []

try:
    set_filter_bar = driver.find_element(By.XPATH, "//*[@id=\"frmSearch\"]/div[1]/div[2]/button")
    set_filter_bar.click()
    set_list = driver.find_element(By.XPATH, "//*[@id=\"cardlist\"]/div[2]/div[2]")
    setElements = set_list.find_elements(By.CLASS_NAME, "selModalClose")
    setList = [el.text for el in setElements]

except Exception as e:
    assert False, f"An error occurred: {e}"

print("Sets trouvés:", setList)

# all_cards = []

# for idx, set_el in enumerate(setElements):
#     # Ouvrir le filtre si ce n'est pas le premier tour
#     if idx > 0:
#         filter_bar = driver.find_element(By.XPATH, "//*[@id=\"frmSearch\"]/div[1]/div[2]/button")
#         filter_bar.click()
#         set_list = driver.find_element(By.XPATH, "//*[@id=\"cardlist\"]/div/div[2]")
#         setElements = set_list.find_elements(By.CLASS_NAME, "selModalClose")
#         set_el = setElements[idx]

#     set_name = set_el.text
#     set_el.click()
#     time.sleep(2)  # Wait for the cards to load

#     # Get all cards in the set
#     cards = driver.find_elements(By.CLASS_NAME, "cardlistItem")
#     for card in cards:
#         try:
#             name = card.find_element(By.CLASS_NAME, "cardName").text
#             all_cards.append(
#                 {
#                     "set": set_name,
#                     "name": name
#                 }
#             )
#         except Exception as e:
#             print(f"Erreur lors de la récupération d'une carte: {e}")

# print(f"Nombre total de cartes récupérées: {len(all_cards)}")
# for card in all_cards[:5]:  # Afficher les 5 premières cartes pour vérification
#     print(card)


