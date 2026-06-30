from pathlib import Path
import sys

# ============================
# PRODUCTS (from models.txt)
# ============================

def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent  # EXE location

    return Path(__file__).resolve().parent  


def _load_products():
    base_path = get_base_path()
    path = base_path / "models" / "models.txt"

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

PRODUCTS = _load_products()

def _load_websites():
    base_path = get_base_path()
    path = base_path / "websites" / "websites.txt"

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

ENABLED_SITES = _load_websites()
# print(PRODUCTS)


# ============================
# PRODUCTS
# ============================

# PRODUCTS = [
#     "GBBS525CPY",
    

#     # "GBBW322AEV", "GBBS726AEV", "GBG5160CEV", "GBBS312AEV", "GBBS322AEV",
#     # "GBBS322APY", "GBBS312BEV", "GBV7280CEV", "GBBS322BEV", "GBBS312APY",
#     # "GBBS322BPY", "GBBS726CEV", "GBBS525CPY", "GBBS322CEV", "GBBS322CPY",
#     # "GBBS514CPY", "GBBS312CEV", "GBBS312CPY", "GBBSJ1CCEP", "GBBSJ1CCPY",
#     # "GBBSJ1CCSW", "GBBSJ20DSW", "GBBSJ11DEP", "GBBSJ10DPY", "GBBSJ10DSW",
#     # "GBBSJ10EEP", "GBBSJ10ESW", "GMG960EVEE", "GMG860EPBE", "GSXE90EVDD",
#     # "GSXE90EVAD", "GSXE91EVAD", "GSXE81EVBD", "GSLE81PYBC", "GSLE91EVAC",
#     # "GSXV80PZLE", "GSLC40PYPE", "GSLC41PYPE", "GSLC40EPPE", "GSLC41EPPE",
#     # "GSGV80EPLD", "GSLE91EVAB", "GSLE81PYBD", "GFM61MCCSF", "GLM71MCCSF",
#     # "LC0R2N2", "F4WR9513S2W", "F4WX851Y", "F4X5511THB", "F4X5011THB",
#     # "F4WX801YB", "F4X5509THB", "F4WX801Y", "F4WX859Y", "F4WX809Y",
#     # "F4X5009THB", "F4X5011TWB", "F4X5009TWB", "GC3R709S1", "F4WR7011SYB",
#     # "F4WR3011S3W", "F4X1009NWB", "F4X1009NWK", "GC3R309S3", "F4X1008NWH",
#     # "F4A1009NWK", "F4DR9537S2W", "F4DR3096N3W", "GD3R509S0", "W4X1095NWB",
#     # "W4X1085NWB", "RT10X8B", "RH90V9AV3N", "RH80V9AV4N", "RH90V5AV6N",
#     # "RT90X8", "RHX5010THB", "RHX5009THB", "RHX5009TWB", "RH18U8AVCW",
#     # "RH90V9ZVEN", "MJ3965ACS", "MJ3965BIB", "MJ3965BPS"
# ]

# ============================
# SESSION SETTINGS
# ============================

SESSION_MIN_ITEMS = 10
SESSION_MAX_ITEMS = 20

SESSION_COOLDOWN_MIN = 10   # seconds
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

OUTPUT_FILE = "Price Tracker.xlsx"

# ============================
# FEATURES / FLAGS
# ============================

# ENABLED_SITES = [
#     "CoolBlue",
#     "MediaMarkt",
#     "OBS",
#     "BOL",
#     "BK"
# ]

MAX_RETRIES = 3
HEADLESS = False
DEBUG = True