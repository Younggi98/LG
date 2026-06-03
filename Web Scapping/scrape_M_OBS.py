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
import re

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

SCRAPED_DATA = []

obs_url = "https://www.lg.com/nl/"
obs_search_url = "https://www.lg.com/nl/search/?tab=product"

""" 
Functions setup the browser with stealth settings to avoid detection
"""

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

""" 
Functions to mimic human behavior and interaction patterns
- random scrolling
- human typing
- retry logic
- cookie acceptance handling
"""
# # random  function to mimic human behavior
# def random_scroll(driver):
#     # perform a few short scrolls to mimic reading
#     for _ in range(random.randint(2, 5)):
#         amount = random.randint(200, 800)
#         driver.execute_script("window.scrollBy(0, arguments[0]);", amount)
#         time.sleep(random.uniform(0.3, 1.0))

def random_scroll(driver):
    # ✅ Step 1: scroll down gradually
    for _ in range(random.randint(2, 5)):
        down_amount = random.randint(300, 900)
        driver.execute_script("window.scrollBy(0, arguments[0]);", down_amount)
        time.sleep(random.uniform(0.4, 1.2))

    # ✅ Step 2: small pause (reading behavior)
    time.sleep(random.uniform(0.8, 2.0))

    # ✅ Step 3: scroll back up slightly (not full reset)
    up_amount = random.randint(200, 600)
    driver.execute_script("window.scrollBy(0, -arguments[0]);", up_amount)

    time.sleep(random.uniform(0.5, 1.2))

    # ✅ Step 4: tiny correction scroll (very human-like)
    micro_adjust = random.randint(-100, 100)
    driver.execute_script("window.scrollBy(0, arguments[0]);", micro_adjust)

   # ✅ Step 3: scroll back to TOP (critical for clickability)
    driver.execute_script("window.scrollTo(0, 0);")

    # ✅ Step 4: small human pause
    time.sleep(random.uniform(0.8, 1.5))



def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def clear_words(element):
    element.send_keys(Keys.CONTROL + "a")  # Select all text
    element.send_keys(Keys.DELETE)          # Delete selected text

def search_model(driver, model):

    try:
        # find search box 
        search_box = driver.find_element(By.ID, "searchbox") #- lg.com

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

def accept_cookies(driver):
    try:
        driver.find_element(By.XPATH, "//button[.='Alles accepteren']").click()

        print("✅ Cookies accepted")
        time.sleep(1)
    except:
        print("No cookie popup found")

# retry finding the element with a few attempts to handle transient loading issues
def find_with_retries(find_func, attempts=3, delay=2):
    last_exc = None
    for attempt in range(attempts):
        try:
            return find_func()
        except Exception as e:
            last_exc = e
            time.sleep(delay * (attempt + 1))
    raise last_exc

# utility function to chunk the list of models into batches for processing
def chunk_list (data, chunk_size):
    """Yield successive chunk_size chunks from data."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def get_product_info(product_text, model):
    pattern = rf'(?<![A-Za-z0-9]){re.escape(model.upper())}(?![A-Za-z0-9.])'
    if not re.search(pattern, product_text.upper()):
        return None

    title = next((line.strip() for line in product_text.splitlines() if line.strip().upper() == model.upper()), model)
    price = next((line.strip() for line in product_text.splitlines() if re.fullmatch(r'€\s*\d[\d.,]*', line.strip())), " ")

    return title, price

# scrap models function
def scrape_model(driver, models,scraped_data):

    time.sleep(1)
    search_model(driver, models)

    if random.random() < 0.5:
        random_scroll(driver)

    price = " "
    
    wait = WebDriverWait(driver, 10)

    results = []

    try :
        products = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "li.c-product-list__item")
        ))

        for product in products:
            product_text = product.text.strip()
            product_info = get_product_info(product_text, models)

            if not product_info:
                continue

            title, price = product_info
            if title and price:
                results.append((title, price))
                print(f"Matched product: {title} | Price: {price}")

    except NoSuchElementException:
        print("Element not found on page \n")

    
    # if not any(d['model'] == models for d in scraped_data):
    #     scraped_data.append({
    #         "model": models,
    #         "price": price,
    #         "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    #     })

#starting the scraping process with batch processing and session management
def process_batch(models_batch):    
    # Choose a random UA and recreate the browser with it
    chosen_ua = random.choice(USER_AGENTS)
    driver = get_browser(user_agent=chosen_ua)
    driver.set_window_size(1080, 800) # set the size of the window  

    for attempt in range(3):
        try:
            print("Opening google page...")
            driver.get("https://www.google.com")  # Start with a neutral page to establish session
            time.sleep(random.uniform(1.5, 2))  
            
            print("Opening obs page...")
            driver.get(obs_url)
            time.sleep(random.uniform(2, 3))  
            accept_cookies(driver)
            # Randomly scroll 
            if random.random() < 0.35:
                random_scroll(driver)
            

            driver.get(obs_search_url)  # Start with a neutral page to establish session
            time.sleep(1)

            break

        except WebDriverException as e:
            print(f"Load attempt {attempt+1} failed: {e}")
            time.sleep(2 * (attempt + 1))
    
    try:
        for model in models_batch:
            start_time = time.perf_counter()

            scrape_model(driver, model, SCRAPED_DATA)

            end_time = time.perf_counter()
            duration = end_time - start_time
            print(f"{model} took {duration:.2f} seconds")
    finally:
        driver.quit()


def main():
    CHUNK_SIZE = 30
    start_time = time.perf_counter()
    
    for i, batch in enumerate(chunk_list(MODELS, CHUNK_SIZE)):
        print(f"\n--- Session {i+1} ---\n")

        process_batch(batch)

        # cooldown between sessions
        time.sleep(random.uniform(15, 30))

    # Save scraped data to excel file
    # scraped_file = "MediaMarkt_Scraped_Data_" + datetime.datetime.now().strftime('%Y-%m-%d') + ".xlsx"
    # with pd.ExcelWriter(scraped_file, engine='openpyxl') as writer:
    #     df = pd.DataFrame(SCRAPED_DATA)
    #     df.to_excel(writer, index=False)
    # print(f"\n📂 Scraping completed: {scraped_file}")

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"Total scraping time: {duration:.2f} seconds")

#run the main function
if __name__ == "__main__":
    main()  




