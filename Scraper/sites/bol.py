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

class site_bol(BaseSite):

    def __init__(self, product_list):
        self.base_url ="https://www.bol.com/nl/"
        super().__init__("BOL", product_list)
        self.initialized = False

    def accept_cookies(self, driver):
        try:
            driver.find_element(By.XPATH, "//button[.='Alles accepteren']").click()
            print("✅ Cookies accepted")
            random_wait(1,2)
        except:
            print("No cookie popup found")

    def accept_settings(self,driver):
        try:
            continue_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.='Doorgaan']"))
            )
            continue_btn.click()
        except:
            print("No popup found")

    def search_model(self, driver, model):
        try:

            search_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchfor"))
            )
            
            # ✅ safe click
            try:
                search_box.click()
            except:
                driver.execute_script("arguments[0].click();", search_box)

            random_wait(0.5, 1.5)
            
            search_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchfor"))
            )

            # clear safely
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)


            human_typing(search_box, model)

            random_wait(1, 2)
            search_box.send_keys(Keys.ENTER)

        except Exception as e:
            print(f"[{self.name}] Search failed: {e}")

    

    def search_product(self, driver, model, retry=False):
        try:
            search_url = f"https://www.bol.com/nl/nl/s/?searchtext={model}"

            if random.random() < 0.01:
                driver.get(self.base_url)

                # handle cookies only when needed
                if not self.initialized:
                    random_wait(2, 3)
                    self.accept_cookies(driver)
                    random_wait(2, 4)
                    self.accept_settings(driver)
                    self.initialized = True

                random_wait(2, 4)

                # optional scroll
                if random.random() < 0.3:
                    random_scroll(driver)

                # perform real typing search
                self.search_model(driver, model)
            else:
                # --- direct URL search (fast + stable) ---
                driver.get(search_url)

                # cookies still needed occasionally
                if not self.initialized:
                    random_wait(2, 3)
                    self.accept_cookies(driver)
                    self.accept_settings(driver)
                    self.initialized = True
                if random.random() < 0.2:
                    random_scroll(driver)

            random_wait(2, 4)
            
            matched_price = " "
            matched_title = None

            try:
                # ✅ wait until product list loads
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//a[contains(@href, '/p/')]")
                    )
                )
                products = driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'md:grid-cols-[2fr_minmax(233px,1fr)]') and .//a[contains(@href, '/p/')]]"
                )

                for p in products[:5]:
                    try:
                        title_el = p.find_element(By.XPATH, ".//a[contains(@href, '/p/') and normalize-space(.)!='']")
                        title = title_el.text.strip()

                        if model.lower() in title.lower():
                            matched_title = title

                            try:
                                card_text = p.text
                                price_match = re.search(r"prijs.*?(\d[\d.\s,]+(?:,\d{2})?)", card_text, re.IGNORECASE)
                                if price_match:
                                    matched_price = price_match.group(1).strip()
                                else:
                                    matched_price = " "
                            except Exception:
                                matched_price = " "

                            break

                    except Exception:
                        continue
                
                # ✅ result handling
                if matched_title:
                    print(f"[{self.name}] Matched product found -> Product: {model} | Price: {matched_price}")
                else:
                    print(f"[{self.name}] No matching product found for {model}")

                return {
                    "site": self.name,
                    "model": model,
                    "price": matched_price,
                }
            except NoSuchElementException:
                print(f"[{self.name}] No results for {model}")

        
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
                "price": " ",
            }
