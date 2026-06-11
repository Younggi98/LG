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

class site_obs(BaseSite):
    
    def __init__(self, product_list):
        self.initialized = False
        super().__init__("OBS", product_list)
        self.base_url = "https://www.lg.com/nl/"
        self.search_url = "https://www.lg.com/nl/search/?tab=product"

    def accept_cookies (self, driver):
        try:
            driver.find_element(By.XPATH, "//button[.='Alles accepteren']").click()
            print("✅ Cookies accepted")
            
        except:
            print("No cookie popup found")

    def search_model(self, driver, model):
        
        try:
            search_box = find_with_retries(
                            lambda: driver.find_element(By.ID, "searchbox"),
                            attempts=3
                        )

            search_box.click()
            random_wait(0.5, 1.5)
            
            search_box = find_with_retries(
                            lambda: driver.find_element(By.ID, "searchbox"),
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
        pattern = rf'(?<![A-Za-z0-9]){re.escape(model.upper())}(?![A-Za-z0-9.])'
        if not re.search(pattern, product_text.upper()):
            return None

        title = next((line.strip() for line in product_text.splitlines() if line.strip().upper() == model.upper()), model)
        price = next((line.strip() for line in product_text.splitlines() if re.fullmatch(r'€\s*\d[\d.,]*', line.strip())), " ")

        return title, price 

    def search_product(self, driver, model):

        try:
            if not self.initialized:
                driver.get(self.search_url)
                random_wait(2, 3)
                self.accept_cookies(driver)
                random_wait(3,4)
                self.initialized = True

            # ✅ optional scroll
            if random.random() < 0.2:
                random_scroll(driver)

             # ✅ search
            self.search_model(driver, model)
            random_wait(2,3)
            matched_price = None

            products = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.c-product-list__item")
            ))

            for product in products:
                product_text = product.text.strip()
                product_info = self.get_product_info(product_text, model)

                if product_info:
                    title, price = product_info
                    matched_price = price
                    print(f"Matched product found -> Product: {title} | Price: {price}")
                    break

            if matched_price is None:
                    print(f"[{self.name}] No matching product found for {model}")

            return {
                    "site": self.name,
                    "model": model,
                    "price": matched_price
                }

        except Exception as e:
            print(f"[{self.name}] Failed: {model} - {e}")

            return {
                "site": self.name,
                "model": model,
                "price": " "
            }
            
        