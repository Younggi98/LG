import re
import random
import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from sites.base_site import BaseSite
from core.human_behavior import (
    random_scroll,
    human_typing,
    find_with_retries,
    random_wait
)


class site_mediamarkt(BaseSite):

    def __init__(self, product_list):
        super().__init__("MediaMarkt", product_list)
        self.base_url = "https://www.mediamarkt.nl/nl/"
        self.initialized = False

    # ==========================
    # INIT
    # ==========================
    def accept_cookies(self, driver):
        try:
            driver.find_element(By.ID, "pwa-consent-layer-accept-all-button").click()
            random_wait(1, 2)
        except:
            pass

    # ==========================
    # SEARCH
    # ==========================
    def search_model(self, driver, model):
        try:
            search_box = driver.find_element(By.ID, "search-form")

            search_box.click()
            random_wait(0.5, 1.5)

            # clear safely
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)

            search_box = find_with_retries(
                            lambda: driver.find_element(By.ID, "search-form"),
                            attempts=3
                        )
            human_typing(search_box, model)

            random_wait(1, 2)
            search_box.send_keys(Keys.ENTER)

            # ✅ wait for results
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="mms-product-card"]'))
            )

        except Exception as e:
            print(f"[{self.name}] Search failed: {e}")

    # ==========================
    # PARSE PRODUCT
    # ==========================

    def get_product_info(self, product_text, model):
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

    # ==========================
    # MAIN FUNCTION (REQUIRED)
    # ==========================
    def search_product(self, driver, model):

        try:
            # ✅ init once per session
            if not self.initialized:
                driver.get(self.base_url)
                random_wait(2, 3)
                self.accept_cookies(driver)
                self.initialized = True

            # ✅ optional scroll
            if random.random() < 0.2:
                random_scroll(driver)

            # ✅ search
            self.search_model(driver, model)
            random_wait(1.5,2.5)
            matched_price = None

            # ✅ no result check
            if driver.find_elements(By.CSS_SELECTOR, '[aria-live="assertive"]'):
                print(f"[{self.name}] No results for {model}")

            else:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="mms-product-card"]'))
                )  

                products = find_with_retries(
                    lambda: driver.find_elements(By.CSS_SELECTOR, '[data-test="mms-product-card"]'),
                    attempts=2
                )


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
                "price": matched_price,
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            }

        except Exception as e:
            print(f"[{self.name}] Failed: {model} - {e}")

            return {
                "site": self.name,
                "model": model,
                "price": None,
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            }