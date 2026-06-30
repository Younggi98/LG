
import json
import random
import time
import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from sites.base_site import BaseSite
from core.human_behavior import random_scroll, human_typing, find_with_retries, random_wait


class site_coolblue(BaseSite):

    def __init__(self, product_list):
        self.initialized = False
        super().__init__("CoolBlue", product_list)
        self.base_url = "https://www.coolblue.nl"

    def accept_cookies (self, driver):
        try:
            driver.find_element(By.CSS_SELECTOR, "button[name='accept_cookie']").click()
            print(" Cookies accepted")
            
        except:
            print("No cookie popup found")
    
    def search_model(self, driver, model):
        
        try:
            search_box = find_with_retries(
                            lambda: driver.find_element(By.NAME, "query"),
                            attempts=3
                        )

            search_box.click()
            random_wait(0.5, 1.5)
            
            search_box = find_with_retries(
                            lambda: driver.find_element(By.NAME, "query"),
                            attempts=3
                        )

            search_box.clear()
            human_typing(search_box, model)

            random_wait(1, 2)
            search_box.send_keys(Keys.ENTER)

        except Exception as e:
            print(f"[{self.name}] Search failed: {e}")

    def search_product(self, driver, model, retry=False):

        try:
            search_url = f"https://www.coolblue.nl/zoeken?query={model}"

            # if random.random() < 0.01:
            #     driver.get(self.base_url)
            #     if not self.initialized:
            #         random_wait(2,3)
            #         self.accept_cookies(driver)
            #         self.initialized = True

            #     random_wait(2, 4)

            #     if random.random() < 0.2:
            #         random_scroll(driver)

            #     self.search_model(driver, model)
            # else:
            driver.get(search_url)
            if not self.initialized:
                random_wait(2,3)
                self.accept_cookies(driver)
                self.initialized = True
                random_wait(2, 4)
            if random.random() < 0.2:
                random_scroll(driver)

            random_wait(2, 4)

            price = None
            product_title = None

            try:

                product_data_div = driver.find_element(By.CSS_SELECTOR, "[data-atc-product-data]")
                title_link = driver.find_element(By.CSS_SELECTOR, ".product-card__title a.link[title]")

                data_str = product_data_div.get_attribute("data-atc-product-data")
                product_title = title_link.get_attribute("title")

                # print(f"[{product_title} | {model} | ")

                is_mismatch = bool(product_title and model.casefold() not in product_title.casefold())

                if is_mismatch:
                    print(f"[{self.name}] No matching product found for {model}")
                    price = " "

                elif data_str:
                    product_data = json.loads(data_str)
                    price = product_data.get("price")
                    print(f"[{self.name}] Matched product found -> Product: {model} | Price: {price}")

                if random.random() < 0.3:
                    random_scroll(driver)

            except NoSuchElementException:
                print(f"[{self.name}] No results for {model}")
                price = " "

            result = {
                "site": self.name,
                "model": model,
                "price": price
            }

            return result

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
                
            return None

