import json
import random
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

# Choose a random UA and recreate the browser with it
chosen_ua = random.choice(USER_AGENTS)
driver = get_browser(user_agent=chosen_ua)
driver.set_window_size(1080, 800) # set the size of the window

models = [
    "GBBS312AEV", "GBBS322AEV", "GBBS322APY", "GBBS312BEV", "GBV7280CEV", 
    "GBBSJ1CCSW", "GBBSJ20DSW", "GBBSJ11DEP", "GSLE91EVAC", "GSXV80PZLE",
    "GBBSJ10DPY", "GBBSJ10DSW", "GBBSJ10EEP", "GBBSJ10ESW", "GMG960EVEE",
    "GMG860EPBE", "GSXE90EVDD", "GSXE90EVAD", "GSXE91EVAD", "GSXE81EVBD",
    "GSLE81PYBC"
]

print(len(models))


cool_blue_url = 'https://www.coolblue.nl'

def random_scroll(driver):
    # perform a few short scrolls to mimic reading
    for _ in range(random.randint(2, 5)):
        amount = random.randint(200, 800)
        driver.execute_script("window.scrollBy(0, arguments[0]);", amount)
        time.sleep(random.uniform(0.3, 1.0))

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

for model in models:
    # Load the page with a few retries on transient errors
    for attempt in range(3):
        try:
            driver.get("https://www.google.com")  # Start with a neutral page to establish session
            time.sleep(random.uniform(2, 4))  # Random delay to mimic human behavior
            driver.get(cool_blue_url)
            # Randomly scroll 
            if random.random() < 0.5:
                random_scroll(driver)

            time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior
            break

        except WebDriverException as e:
            print(f"Load attempt {attempt+1} failed: {e}")
            time.sleep(2 * (attempt + 1))

    model_url = f'https://www.coolblue.nl/zoeken?query={model}'
    print(f"Searching: {model}\n")
    print(f"Model: {model} | URL: {model_url}")
    driver.get(model_url)

    time.sleep(random.uniform(2, 4))  # Random delay to mimic human behavior

    # Randomly scroll 
    if random.random() < 0.5:
        random_scroll(driver)

    try:
        # Find element with retries
        product_data_div = find_with_retries(lambda: driver.find_element(By.CSS_SELECTOR, "[data-atc-product-data]"), attempts=3, delay=1)
        title_link = find_with_retries(lambda: driver.find_element(By.CSS_SELECTOR, ".product-card__title a.link[title]"), attempts=3, delay=1)
        
        # Extract the JSON data from the attribute
        data_str = product_data_div.get_attribute("data-atc-product-data")

        # extract the title attribute
        product_title = title_link.get_attribute("title")
        print("Title:", product_title)

        # if title doesnt match with model, flag it and skip to next model
        if model.lower() not in product_title.lower():
            print(f"Warning: Product title '{product_title}' does not match expected model '{model}' \n")
            time.sleep(random.uniform(4, 10))
            # go to next model
            continue
        
        # Flag if attribute is empty
        if not data_str or data_str.strip() == "":
            print("Flag: data-atc-product-data attribute is empty \n ")
            product_data = {}
        else:
            product_data = json.loads(data_str)

        price = product_data.get("price") if product_data else None
        product_id = product_data.get("productIds", [None])[0] if product_data else None

        print(f"Product Model: {model} | Product ID: {product_id} | Price: {price}")

    except NoSuchElementException:
        print("Element not found on page \n")

    time.sleep(random.uniform(4, 10))

driver.quit()