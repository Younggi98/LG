import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

from config import USER_AGENTS, HEADLESS


# ===========================
# CREATE BROWSER
# ===========================

def create_browser():
    """
    Creates a new browser instance with:
    - Random user agent
    - Stealth mode
    - Anti-detection settings
    """

    # ✅ choose random user agent
    user_agent = random.choice(USER_AGENTS)

    options = Options()

    # ---------------------------
    # BASIC CONFIG
    # ---------------------------
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    options.add_argument(f"--user-agent={user_agent}")

    if HEADLESS:
        options.add_argument("--headless=new")

    # ✅ optional: random window size (more human-like)
    width = random.randint(1000, 1400)
    height = random.randint(700, 1000)
    options.add_argument(f"--window-size={width},{height}")

    # ---------------------------
    # CREATE DRIVER
    # ---------------------------
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # ---------------------------
    # STEALTH MODE (IMPORTANT)
    # ---------------------------
    stealth(
        driver,
        user_agent=user_agent,
        languages=["nl-NL", "nl"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        run_on_insecure_origins=False,
    )

    # ---------------------------
    # REMOVE webdriver FLAG
    # ---------------------------
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        }
    )

    return driver