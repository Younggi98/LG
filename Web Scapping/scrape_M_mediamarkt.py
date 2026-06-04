import json
from pyexpat import model
import random
from turtle import title
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

# List of models to scrape, wrap all in quotes and separate by comma
MODELS = [
"GBBS525CPY",

"F4WX801YB",
"F4X5509THB",
"F4WX801Y",
"F4WX859Y",
"MJ3965BIB",
"MJ3965BPS"
]

SCRAPED_DATA = []

media_markt_url = "https://www.mediamarkt.nl/nl/"

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
# random  function to mimic human behavior
def random_scroll(driver):
    # perform a few short scrolls to mimic reading
    for _ in range(random.randint(2, 5)):
        amount = random.randint(200, 800)
        driver.execute_script("window.scrollBy(0, arguments[0]);", amount)
        time.sleep(random.uniform(0.3, 1.0))

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
        #search_box = driver.find_element(By.NAME, "query")
        search_box = driver.find_element(By.ID, "search-form") 

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
        #driver.find_element(By.CSS_SELECTOR, "button[name='accept_cookie']").click()
        driver.find_element(By.ID, "pwa-consent-layer-accept-all-button").click()

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
    model_code = model.upper().strip()
    pattern = rf'(?<![A-Za-z0-9]){re.escape(model_code)}(?![A-Za-z0-9])'

    if not re.search(pattern, product_text.upper()):
        return None
        

    lines = [line.strip() for line in product_text.splitlines() if line.strip()]
    title = next((line for line in lines if re.search(pattern, line.upper())), model_code)

    promo_words = r'cashback|korting|promo|actie|besparing|save|voordeel'
    price_candidates = []

    for line in lines:
        if re.search(promo_words, line, flags=re.IGNORECASE):
            continue

        for match in re.finditer(r'€\s*\d[\d.,–-]*', line):
            price_candidates.append((line, match.group(0)))

    def normalize_price(text):
        cleaned = text.replace('€', '', 1)
        cleaned = cleaned.replace('.', '').replace(',', '.').replace('–', '').replace('-', '').strip()
        return float(cleaned) if cleaned else float('inf')

    discounted_candidates = [(line, price) for (line, price) in price_candidates if re.search(r'\bnu\b', line, flags=re.IGNORECASE)]

    if discounted_candidates:
        _, price = min(discounted_candidates, key=lambda item: normalize_price(item[1]))
    elif price_candidates:
        _, price = max(price_candidates, key=lambda item: normalize_price(item[1]))
    else:
        price = " "

    return title, price


# scrap models function
def scrape_model(driver, models,scraped_data):

    time.sleep(1)
    search_model(driver, models)

    if random.random() < 0.5:
        random_scroll(driver)

    matched_price = " "
    time.sleep(2)

    #if driver.find_elements(By.CSS_SELECTOR, '[aria-live = "assertive"]'): then it means no results found, so we can skip to next model
    if driver.find_elements(By.CSS_SELECTOR, '[aria-live = "assertive"]'):
        print(f"No results found for model {models} \n")
        scraped_data.append({
                    "model": models,
                    "price": matched_price,
                    "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        return
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="mms-product-card"]'))
        )  
        # Find element with retries
        # product_data_div = find_with_retries(lambda: driver.find_element(By.CSS_SELECTOR, "[data-atc-product-data]"), attempts=1, delay=0)
        # title_link = find_with_retries(lambda: driver.find_element(By.CSS_SELECTOR, ".product-card__title a.link[title]"), attempts=3, delay=1)
    
        # data_str = product_data_div.get_attribute("data-atc-product-data")
        # product_title = title_link.get_attribute("title")

        products = find_with_retries(lambda: driver.find_elements(By.CSS_SELECTOR, '[data-test="mms-product-card"]'), attempts=1, delay=0)

        for product in products:
            print(product.text)
            product_text = product.text.strip()
            product_info = get_product_info(product_text, models)
            
            if product_info:
                title, price = product_info
                matched_price = price
                print(f"Matched product found -> Product: {title} | Price: {price}")
                break
            else:
                print(f"No matching product found for model '{models}' in the following text:\n{product_text}\n")

            # if models.lower() not in title.lower():
            #     print(f"Warning: Product title '{title}' does not match expected model '{models}' \n")
            # else:
            #     print(f"Product: {title} | Price: {price}")
            #     break

        # if title doesnt match with model, flag it and skip to next model
        # if models.lower() not in product_title.lower():
        #     print(f"Warning: Product title '{product_title}' does not match expected model '{models}' \n")
        # else:
        #     if data_str and data_str.strip():
        #         product_data = json.loads(data_str)
        #         price = product_data.get("price", " ")

        scraped_data.append({
                    "model": models,
                    "price": matched_price,
                    "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

    except NoSuchElementException:
        print("Element not found on page \n")

    
    if not any(d['model'] == models for d in scraped_data):
        scraped_data.append({
            "model": models,
            "price": matched_price,
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

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
            
            print("Opening media markt page...")
            driver.get(media_markt_url)
            time.sleep(random.uniform(2, 3))  
            accept_cookies(driver)

            # Randomly scroll 
            if random.random() < 0.5:
                random_scroll(driver)
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
    CHUNK_SIZE = 20
    start_time = time.perf_counter()
    
    for i, batch in enumerate(chunk_list(MODELS, CHUNK_SIZE)):
        print(f"\n--- Session {i+1} ---\n")

        process_batch(batch)

        # cooldown between sessions
        time.sleep(random.uniform(15, 30))

    scraped_file = "MediaMarkt_Scraped_Data_" + datetime.datetime.now().strftime('%Y-%m-%d') + ".xlsx"

    with pd.ExcelWriter(scraped_file, engine='openpyxl') as writer:
        df = pd.DataFrame(SCRAPED_DATA)
        df.to_excel(writer, index=False)
    print(f"\n📂 Scraping completed: {scraped_file}")

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"Total scraping time: {duration:.2f} seconds")

#run the main function
if __name__ == "__main__":
    main()  




