import random
import time

from core.browser import create_browser
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from core.human_behavior import random_wait

from config import (
    SESSION_MIN_ITEMS,
    SESSION_MAX_ITEMS,
    SESSION_COOLDOWN_MIN,
    SESSION_COOLDOWN_MAX
)

def run_with_timeout(func, timeout, *args):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args)
        return future.result(timeout=timeout)

class SessionManager:

    def __init__(self, sites, result_handler):
        self.sites = sites
        self.result_handler = result_handler
        self.site_index = 0  # track rotation
        self.total_products = sum(len(site.product_list) for site in sites)
        self.processed_products = 0

    # =================================
    # MAIN LOOP CONTROLLER
    # =================================
    def run(self):
        session_count = 1
        Max_sessions = 300

        while not self._all_sites_completed():
            
            if session_count > Max_sessions:
                print("⚠️ Forced stop (safety)")
                break

            print(f"\n===== SESSION {session_count} =====\n")

            site = self._get_next_site()

            if site is None:
                print("All sites completed.")
                break

            # ✅ NEW: double-check
            if site.is_done():
                continue

            self._run_single_session(site)
            
            if self._all_sites_completed():
                print("✅ All scraping finished early.")
                break

            session_count += 1

            # cooldown between sessions
            sleep_time = random.randint(
                SESSION_COOLDOWN_MIN,
                SESSION_COOLDOWN_MAX
            )
            print(f"Cooldown: {sleep_time}s\n")
            time.sleep(sleep_time)

    # =================================
    # RUN ONE SESSION (1 SITE)
    # =================================
    def _run_single_session(self, site):

        print(f"Running site: {site.name}")

        site.initialized = False
        
        batch_size = random.randint(
            SESSION_MIN_ITEMS,
            SESSION_MAX_ITEMS
        )

        remaining = site.get_remaining_products()

        if not remaining:
            print(f"{site.name} already completed")
            return

        batch = remaining[:batch_size]

        # ✅ Create new browser (same behavior as your script)
        driver = create_browser()

        try:
            for product in batch:
                start_time = time.perf_counter()

                max_retries = 2
                attempt = 0
                result = None
                
                while attempt <= max_retries:
                    attempt += 1
                    try:
                        result = run_with_timeout(
                            site.search_product,
                            30,
                            driver,
                            product
                        )
                        break
                    except TimeoutError:
                        print(f"[TIMEOUT] {product} → retry {attempt}/{max_retries}")

                        try:
                            driver.quit()
                        except:
                            pass

                        driver = create_browser()

                        if attempt > max_retries:
                            result = None
                        
                    # result = site.search_product(driver, product)

                self.processed_products += 1
                
                if result:
                    self.result_handler.add(result)
                    site.mark_completed(product)
                    status = "OK"
                else:
                    status = "FAILED"


                duration = time.perf_counter() - start_time
                print(f"[{self.processed_products}/{self.total_products}] {site.name} | {status} | {product} | {duration:.2f}s")

        finally:
            driver.quit()

    # =================================
    # SITE ROTATION LOGIC
    # =================================
    def _get_next_site(self):
        checked = 0

        while checked < len(self.sites):
            site = self.sites[self.site_index]

            self.site_index = (self.site_index + 1) % len(self.sites)
            checked += 1

            if not site.is_done():
                return site

        return None  # all done

    # =================================
    # COMPLETION CHECK
    # =================================
    def _all_sites_completed(self):
        return all(site.is_done() for site in self.sites)
    