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
    "GBG5160CEV",
    "GBBS312AEV",
    "GBBS322AEV",
    "GBBS322APY",
    "GBBS312BEV",
    "GBV7280CEV",
    "GBBS322BEV",
    "GBBS312APY",
    "GBBS322BPY",
    "GBBS726CEV",
    "GBBS525CPY",
    "GBBS322CEV",
    "GBBS322CPY",
    "GBBS514CPY",
    "GBBS312CEV",
    "GBBS312CPY",
    "GBBSJ1CCEP",
    "GBBSJ1CCPY",
    "GBBSJ1CCSW",
    "GBBSJ20DSW",
    "GBBSJ11DEP",
    "GBBSJ10DPY",
    "GBBSJ10DSW",
    "GBBSJ10EEP",
    "GBBSJ10ESW",
    "GMG960EVEE",
    "GMG860EPBE",
    "GSXE90EVDD",
    "GSXE90EVAD",
    "GSXE91EVAD",
    "GSXE81EVBD",
    "GSLE81PYBC",
    "GSLE91EVAC",
    "GSXV80PZLE",
    "GSLC40PYPE",
    "GSLC41PYPE",
    "GSLC40EPPE",
    "GSLC41EPPE",
    "GSGV80EPLD",
    "GSLE91EVAB",
    "GSLE81PYBD",
    "GFM61MCCSF",
    "GLM71MCCSF",
    "LC0R2N2",
    "F4WR9513S2W",
    "F4WX851Y",
    "F4X5511THB",
    "F4X5011THB",
    "F4WX801YB",
    "F4X5509THB",
    "F4WX801Y",
    "F4WX859Y",
    "F4WX809Y",
    "F4X5009THB",
    "F4X5011TWB",
    "F4X5009TWB",
    "GC3R709S1",
    "F4WR7011SYB",
    "F4WR3011S3W",
    "F4X1009NWB",
    "F4X1009NWK",
    "GC3R309S3",
    "F4X1008NWH",
    "F4A1009NWK",
    "F4DR9537S2W",
    "F4DR3096N3W",
    "GD3R509S0",
    "W4X1095NWB",
    "W4X1085NWB",
    "RT10X8B",
    "RH90V9AV3N",
    "RH80V9AV4N",
    "RH90V5AV6N",
    "RT90X8",
    "RHX5010THB",
    "RHX5009THB",
    "RHX5009TWB",
    "RH18U8AVCW",
    "RH90V9ZVEN",
    "MJ3965ACS",
    "MJ3965BIB",
    "MJ3965BPS"
]

SCRAPED_DATA = []

cool_blue_url = 'https://www.coolblue.nl'

# random scroll function to mimic human behavior
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

def search_model(driver, model):

    try:
        # find search box 
        search_box = driver.find_element(By.NAME, "query")

        # click into it
        search_box.click()
        time.sleep(random.uniform(0.5, 1.5))

        # clear existing text
        search_box.clear()

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
        driver.find_element(By.CSS_SELECTOR, "button[name='accept_cookie']").click()
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

# scrap models function
def scrape_model(driver, models,scraped_data):
     
    model_url = f'https://www.coolblue.nl/zoeken?query={models}'
    # print(f"Searching: {models}\n")
    # print(f"Model: {models} | URL: {model_url}")
    #driver.get(model_url)

    product_id = "Unknown"
    price = "Unknown"

    time.sleep(1)
    search_model(driver, models)

    if random.random() < 0.5:
        random_scroll(driver)
    
    try:
        # Find element with retries
        product_data_div = find_with_retries(lambda: driver.find_element(By.CSS_SELECTOR, "[data-atc-product-data]"), attempts=1, delay=0)
        title_link = find_with_retries(lambda: driver.find_element(By.CSS_SELECTOR, ".product-card__title a.link[title]"), attempts=3, delay=1)
        
        # Extract the JSON data from the attribute - price data is here
        data_str = product_data_div.get_attribute("data-atc-product-data")

        # extract the title attribute - model name is here
        product_title = title_link.get_attribute("title")

        # if title doesnt match with model, flag it and skip to next model
        if models.lower() not in product_title.lower():
            print(f"Warning: Product title '{product_title}' does not match expected model '{models}' \n")
        else:
            if data_str and data_str.strip():
                product_data = json.loads(data_str)
                price = product_data.get("price", "Unknown")

    except NoSuchElementException:
        print("Element not found on page \n")

    
    if not any(d['model'] == models for d in scraped_data):
        scraped_data.append({
            "model": models,
            "price": price,
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

def process_batch(models_batch):    
    # Choose a random UA and recreate the browser with it
    chosen_ua = random.choice(USER_AGENTS)
    driver = get_browser(user_agent=chosen_ua)
    driver.set_window_size(1080, 800) # set the size of the window  

    for attempt in range(3):
        try:
            driver.get("https://www.google.com")  # Start with a neutral page to establish session
            time.sleep(random.uniform(1.5, 2))  # Random delay to mimic human behavior
            driver.get(cool_blue_url)
            time.sleep(random.uniform(2, 3))  # Random delay to mimic human behavior
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
    CHUNK_SIZE = 30
    start_time = time.perf_counter()
    
    for i, batch in enumerate(chunk_list(MODELS, CHUNK_SIZE)):
        print(f"\n--- Session {i+1} ---\n")

        process_batch(batch)

        # cooldown between sessions
        time.sleep(random.uniform(15, 30))

    # Save scraped data to excel file
    scraped_file = "CoolBlue_Scraped_Data_" + datetime.datetime.now().strftime('%Y-%m-%d') + ".xlsx"
    with pd.ExcelWriter(scraped_file, engine='openpyxl') as writer:
        df = pd.DataFrame(SCRAPED_DATA)
        df.to_excel(writer, index=False)
    print(f"\n📂 Scraping completed: {scraped_file}")

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"{model} took {duration:.2f} seconds")

#run the main function
if __name__ == "__main__":
    main()  