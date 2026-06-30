import re
import json
import random
import time
import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sites.base_site import BaseSite
from core.human_behavior import random_scroll, human_typing, find_with_retries, random_wait

class site_bk(BaseSite):
    
    def __init__(self, product_list):
        self.initialized = False
        super().__init__("BK", product_list)
        self.base_url = "https://www.bemmelenkroon.nl/"
        

    def accept_cookies (self, driver):
        try:
            driver.find_element(By.CSS_SELECTOR,"div.CookiebotConsent-actions button").click()
            print(" Cookies accepted")
            
        except:
            print("No cookie popup found")

    def search_model(self, driver, model):
        
        try:
            search_box = find_with_retries(
                            lambda: driver.find_element(By.ID, "siteSearch-input"),
                            attempts=3
                        )

            search_box.click()
            random_wait(0.5, 1.5)
            
            search_box = find_with_retries(
                            lambda: driver.find_element(By.ID, "siteSearch-input"),
                            attempts=3
                        )

            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)

            human_typing(search_box, model)

            random_wait(1, 2)
            search_box.send_keys(Keys.ENTER)

        except Exception as e:
            print(f"[{self.name}] Search failed: {e}")

    def get_product_info(self, product_text, model):
        if any("geen resultaten voor" in l.lower() for l in product_text):
            print(f"[{self.name}] No results found for {model}")
            return {
                "model": model,
                "price": " "
            }

        cleaned_lines = [l.strip() for l in product_text if l.strip()]

        if not any(model.casefold() in line.casefold() for line in cleaned_lines):
            print(f"[{self.name}] No matching product found for {model}")
            return None

        price = " "
        price_pattern = r'€?\s*\d[\d.\s]*(?:,\d{2}|,-)'

        for i, line in enumerate(cleaned_lines):
            lowered = line.lower()

            if any(x in lowered for x in ["cashback", "adviesprijs", "meestal"]):
                continue

            price_match = re.search(price_pattern, line)
            if not price_match:
                continue

            candidate = price_match.group(0).replace("€", "").replace(" ", "").strip()

            if i > 0 and "cashback" in cleaned_lines[i - 1].lower():
                continue

            if candidate and candidate != "":
                price = candidate

        return {
            "model": model,
            "price": price
        }

    def search_product(self, driver, model, retry = False):

        try:
            search_url = f"https://www.bemmelenkroon.nl/zoeken/?query={model}"

            # if random.random() < 0.01:
            #     driver.get(self.base_url)
            #     if not self.initialized:
            #         random_wait(2, 3)
            #         self.accept_cookies(driver)
            #         self.initialized = True

            #     random_wait(2, 4)

            #      # optional scroll
            #     if random.random() < 0.3:
            #         random_scroll(driver)

            #     # ✅ search
            #     self.search_model(driver, model)
            
            # else:
            driver.get(search_url)
            if not self.initialized:
                random_wait(2, 3)
                self.accept_cookies(driver)
                self.initialized = True
            if random.random() < 0.2:
                random_scroll(driver)

            random_wait(2, 4)
            found = False
            matched_price = None

            products = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.ProductsOverview-items")
            ))

            for product in products:
                product_text = product.text.split("\n")

                if any("geen resultaten voor" in l.lower() for l in product_text):
                    print(f"[{self.name}] No results found for {model}")

                    return {
                        "site": self.name,
                        "model": model,
                        "price": " ",
                    }
                
                # ✅ Extract info
                result = self.get_product_info(product_text, model)
                
                if result is not None:
                    found = True
                    matched_price = result.get("price", " ")

                    print(f"[{self.name}] Matched product found -> Product: {model} | Price: {matched_price}")
                    return {
                        "site": self.name,
                        "model": model,
                        "price": matched_price
                    }
            
            if not found:
                print(f"[{self.name}] No matching product found for {model}")
                matched_price = " "

            return {
                    "site": self.name,
                    "model": model,
                    "price": matched_price
                }

        except Exception as e:
            print(f"[{self.name}] Failed: {model} - {e}")

            if not retry:
                print(f"[{self.name}] Retrying once...")
                try:
                    driver.refresh()
                    random_wait(2, 4)
                    return self.search_product(driver, model, retry=True)
                except Exception as e2:
                    print(f"[{self.name}] Retry failed: {model} - {e2}")

            return {
                "site": self.name,
                "model": model,
                "price": " "
            }
            
        