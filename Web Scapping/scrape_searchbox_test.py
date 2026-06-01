import json
from pyexpat import model
import random
import pandas as pd
from xml.parsers.expat import model
import time
import openpyxl
import datetime
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




# List of example User-Agents for rotation (add more as needed)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]

# List of models to scrape
MODELS = [
    "GBBW322AEV",
    "GBBS726AEV",
    "GBG5160CEV"
]
bol_url = "https://www.bol.com/nl"


def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def clear_words(element):
    element.send_keys(Keys.CONTROL + "a")  # Select all text
    element.send_keys(Keys.DELETE)          # Delete selected text

def get_browser(user_agent = None):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Set the user agent if provided (rotation)
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options) #Opens Chrome

    # make it slient so that it won't show "Chrome is being controlled by automated test software"
    stealth(
        driver,
        user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        languages= ["nl-NL", "nl"], 
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        run_on_insecure_origins= False,
    )

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    return driver


def accept_cookies(driver):
    try:
        #driver.find_element(By.CSS_SELECTOR, "button[name='accept_cookie']").click()  - Coolblue
        #driver.find_element(By.ID, "pwa-consent-layer-accept-all-button").click()     #- media markt
        #driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
        driver.find_element(By.XPATH, "//button[.='Alles accepteren']").click()

        print("✅ Cookies accepted")
        time.sleep(1)
    except:
        print("No cookie popup found")

def search_model(driver, model):
    try:
        # find search box 
        #search_box = driver.find_element(By.NAME, "query") - Coolblue
        #search_box = driver.find_element(By.ID, "search-form") #- media markt
        #search_box = driver.find_element(By.NAME, "query") # - expert.com
        search_box = driver.find_element(By.ID, "searchfor") #- bol.com

        # click into it
        search_box.click()
        time.sleep(random.uniform(0.5, 1.5))

        # clear existing text
        clear_words(search_box)

        # type model like human
        human_typing(search_box, model)

        time.sleep(random.uniform(1, 2))

        # press Enter
        search_box.send_keys(Keys.ENTER)

        # wait for results
        time.sleep(random.uniform(1, 2))

    except Exception as e:
        print(f"Search failed: {e}")

driver = get_browser()
driver.get(bol_url)
time.sleep(2)
accept_cookies(driver)
time.sleep(2.5)

for model in MODELS:
    search_model(driver, model)
    time.sleep(5)  # wait before next search    

driver.close()