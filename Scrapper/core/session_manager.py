import random
import time

from core.browser import create_browser
from core.human_behavior import random_wait

from config import (
    SESSION_MIN_ITEMS,
    SESSION_MAX_ITEMS,
    SESSION_COOLDOWN_MIN,
    SESSION_COOLDOWN_MAX
)

class SessionManager:

    def __init__(self, sites, result_handler):
        self.sites = sites
        self.result_handler = result_handler
        self.site_index = 0  # track rotation

    # =================================
    # MAIN LOOP CONTROLLER
    # =================================
    def run(self):
        session_count = 1

        while not self._all_sites_completed():
            print(f"\n===== SESSION {session_count} =====\n")

            site = self._get_next_site()

            if site is None:
                print("All sites completed.")
                break

            self._run_single_session(site)

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

                result = site.search_product(driver, product)

                if result:
                    self.result_handler.add(result)
                    site.mark_completed(product)

                duration = time.perf_counter() - start_time
                print(f"{product} took {duration:.2f}s")

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