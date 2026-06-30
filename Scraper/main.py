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
import os


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

    if "OBS" in ENABLED_SITES:
        sites.append(site_obs(PRODUCTS)) 

    if "BK" in ENABLED_SITES:
        sites.append(site_bk(PRODUCTS))

    if "Expert" in ENABLED_SITES:
        sites.append(site_bk(PRODUCTS))

    if "BOL" in ENABLED_SITES:
        sites.append(site_bol(PRODUCTS))

    return sites


# ===========================
# MAIN PROGRAM
# ===========================

def main():
    # ✅ Start timer
    start_time = time.time()

    print("\nStarting scraping...\n")
    print("Progress will be shown live in this console window.\n")

    # ✅ create site instances
    sites = create_sites()

    if not sites:
        print("No sites enabled. Check config.ENABLED_SITES")
        return

    # ✅ result manager
    result_handler = ResultHandler()

    # ✅ session manager
    manager = SessionManager(sites, result_handler)

    # ✅ run scraping
    manager.run()

    # ✅ save final results
    result_handler.save()

    print("\n Scraping completed.\n")

    # ✅ End timer
    end_time = time.time()
    elapsed = end_time - start_time

    # ✅ Pretty format
    elapsed_str = str(datetime.timedelta(seconds=int(elapsed)))

    print(f"\n Total execution time: {elapsed_str}\n")


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)  # EXE location
    return os.path.dirname(os.path.abspath(__file__))  # dev 



# ===========================
# ENTRY POINT
# ===========================

if __name__ == "__main__":
    
    BASE_PATH = get_base_path()

    # ✅ Create /log folder next to EXE
    LOG_PATH = os.path.join(BASE_PATH, "log")
    os.makedirs(LOG_PATH, exist_ok=True)

    # ✅ Log filename with timestamp
    log_filename = f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    log_full_path = os.path.join(LOG_PATH, log_filename)

    # ✅ Redirect stdout
    sys.stdout = Tee(log_full_path)

    print(f" Logging to file: {log_full_path}")


    main()