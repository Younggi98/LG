from config import PRODUCTS, ENABLED_SITES
from core.session_manager import SessionManager
from core.result_handler import ResultHandler

# ✅ import your sites
from sites.coolblue import site_coolblue
from sites.mediamarkt import site_mediamarkt
# from sites.site_bol import BolSite


# ===========================
# INITIALIZE SITES
# ===========================

def create_sites():
    sites = []

    # if "CoolBlue" in ENABLED_SITES:
    #     sites.append(site_coolblue(PRODUCTS))

    if "MediaMarkt" in ENABLED_SITES:
        sites.append(site_mediamarkt(PRODUCTS))

    # if "Bol" in ENABLED_SITES:
    #     sites.append(BolSite(PRODUCTS))

    return sites


# ===========================
# MAIN PROGRAM
# ===========================

def main():
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


# ===========================
# ENTRY POINT
# ===========================

if __name__ == "__main__":
    main()