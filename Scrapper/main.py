from config import PRODUCTS, ENABLED_SITES
from core.session_manager import SessionManager
from core.result_handler import ResultHandler

# ✅ import your sites
from sites.coolblue import site_coolblue
from sites.mediamarkt import site_mediamarkt
from sites.obs import site_obs
from sites.bol import site_bol
from sites.bk import site_bk

import sys
import datetime
import time

# ===========================
# LOGGING (TEE: console + file)
# ===========================

class Tee:
    def __init__(self, filename):
        self.file = open(filename, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, message):
        self.stdout.write(message)
        self.file.write(message)

    def flush(self):
        self.stdout.flush()
        self.file.flush()


# ===========================
# INITIALIZE SITES
# ===========================

def create_sites():
    sites = []

    if "CoolBlue" in ENABLED_SITES:
        sites.append(site_coolblue(PRODUCTS))

    if "MediaMarkt" in ENABLED_SITES:
        sites.append(site_mediamarkt(PRODUCTS))

    if "BOL" in ENABLED_SITES:
        sites.append(site_bol(PRODUCTS))

    if "OBS" in ENABLED_SITES:
        sites.append(site_obs(PRODUCTS)) 

    if "B&K" in ENABLED_SITES:
        sites.append(site_bk(PRODUCTS))

    return sites


# ===========================
# MAIN PROGRAM
# ===========================

def main():
    # ✅ Start timer
    start_time = time.time()

    print("\n🚀 Starting scraping system...\n")

    # ✅ create site instances
    sites = create_sites()

    if not sites:
        print("❌ No sites enabled. Check config.ENABLED_SITES")
        return

    # ✅ result manager
    result_handler = ResultHandler()

    # ✅ session manager
    manager = SessionManager(sites, result_handler)

    # ✅ run scraping
    manager.run()

    # ✅ save final results
    result_handler.save()

    print("\n✅ Scraping completed.\n")

    # ✅ End timer
    end_time = time.time()
    elapsed = end_time - start_time

    # ✅ Pretty format
    elapsed_str = str(datetime.timedelta(seconds=int(elapsed)))

    print(f"\n⏱ Total execution time: {elapsed_str}\n")


# ===========================
# ENTRY POINT
# ===========================

if __name__ == "__main__":
    # ✅ Create log file
    log_filename = f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    sys.stdout = Tee(log_filename)

    print(f"📝 Logging to file: {log_filename}")

    main()