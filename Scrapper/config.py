# ============================
# PRODUCTS
# ============================

PRODUCTS = [
    "GSXE91EVAD",
    "GSXE81EVBD",
    "GSLE81PYBC",
    "GSLE91EVAC",
    "GSXV80PZLE",
    "GSLC40PYPE"

    # ... rest of your models
]

# ============================
# SESSION SETTINGS
# ============================

SESSION_MIN_ITEMS = 5
SESSION_MAX_ITEMS = 10

SESSION_COOLDOWN_MIN = 2   # seconds
SESSION_COOLDOWN_MAX = 15

# ============================
# BROWSER SETTINGS
# ============================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]

# ============================
# OUTPUT
# ============================

OUTPUT_FILE = "scraped_results.xlsx"

# ============================
# FEATURES / FLAGS
# ============================

ENABLED_SITES = [
    "CoolBlue",
    "MediaMarkt"
]

MAX_RETRIES = 3
HEADLESS = False
DEBUG = True