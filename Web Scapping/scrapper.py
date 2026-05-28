import json
import random
import time
import openpyxl
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

def get_browser():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options) #Opens Chrome

    # make it slient so that it won't show "Chrome is being controlled by automated test software"
    stealth(
        driver,
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
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

# This script collects TV product listings from BestBuy Canada
# It navigates the site's JSON search API using Selenium, parses
# the JSON response, filters out refurbished/open-box items,
# and saves cleaned results into an Excel file.

wb = openpyxl.Workbook()
sheet = wb.active
sheet.append(["Brand", "Model", "Inch", "Desc", "Regular Price", "Sale Price"])

driver = get_browser()
i = 1
finished = False
totalPage = 1

try:
    while not finished:
        # Build the API search URL for the current page
        base_url = "https://www.bestbuy.ca/api/v2/json/search?"
        category = "categoryid=20003"  # TV category
        current_region = "&currentRegion=ON&include=facets%2C%20redirects"
        path = "&path=category%3ATV%20%26%20Home%20Theatre%3Bcategory%3ATelevisions%3BbrandName%3ASAMSUNG%7CLG%7CSONY%3Bsoldandshippedby0enrchstring%3ABest%20Buy"
        lang = "&lang=en-CA"
        current_page = "&page=" + str(i)
        search_url = base_url + category + current_region + lang + current_page + path

        # Informational print and request the URL
        print(f"page: {i}/{totalPage if i > 1 else '?'}")
        driver.get(search_url)

        # Wait a bit for the JSON response to load (more for first page)
        wait_time = 10 if i == 1 else 7
        time.sleep(wait_time)

        #read <pre> tag if exists, otherwise read <body> tag
        # The API response is usually shown as plain text inside a <pre>
        # If not, read the whole <body> as a fallback
        try:
            raw_content = driver.find_element(By.TAG_NAME, "pre").text
        except:
            raw_content = driver.find_element(By.TAG_NAME, "body").text

        # Parse JSON; if parsing fails we were likely blocked or received HTML
        try:
            json_obj = json.loads(raw_content)
        except Exception as e:
            print(f"Failed parsing JSON: {e}")
            driver.save_screenshot(f"blocked_page_{i}.png")
            break

        # On the first page record how many pages are available
        if i == 1:
            totalPage = json_obj.get("totalPages", 1)

        print(f"Page: {json_obj.get('currentPage')} / {totalPage}")

        # Loop through products and extract fields we care about
        for product in json_obj.get("products", []):
            parsed_name = product["name"]
            parsed_regularPrice = product["regularPrice"]
            parsed_salePrice = product["salePrice"]

            # Skip open-box or refurbished items based on keywords
            excludeStr = ["Open Box", "Refurbished", "(Good)", "(Excellent)"]
            if any([x in parsed_name for x in excludeStr]):
                print(f"[X] {parsed_name}")
            else:
                # Print a simple, friendly line for each valid product
                print(f"✅ {parsed_name} | {parsed_regularPrice} | {parsed_salePrice}")
                try:
                    # Try to parse a model inside parentheses
                    model = parsed_name.split("(")[1].split(")")[0] if "(" in parsed_name else ""
                    # Brand is taken as the first word of the name
                    brand = parsed_name.split(" ")[0]
                    # Inch value often appears before a double-quote character
                    inch = parsed_name.split('"')[0].split(" ")[-1] if '"' in parsed_name else ""
                    sheet.append([brand, model, inch, parsed_name, parsed_regularPrice, parsed_salePrice])
                except:
                    # If parsing fails, still save the basic info
                    sheet.append(["", "", "", parsed_name, parsed_regularPrice, parsed_salePrice])

        # Move to the next page and stop when we've reached the last one
        i += 1
        if i > totalPage:
            finished = True

        # Sleep a short random time to mimic human browsing and reduce blocking risk
        time.sleep(random.uniform(2, 5))


finally:
    driver.quit()

xl_file = "BBY-Pricing-TV-" + datetime.datetime.now().strftime('%Y-%m-%d') + ".xlsx"
wb.save(xl_file)
print(f"\n📂 작업 완료: {xl_file}")

