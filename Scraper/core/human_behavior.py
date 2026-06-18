import time
import random
from selenium.webdriver.common.keys import Keys

# ===========================
# WAIT (basic building block)
# ===========================

def random_wait(min_sec=1.0, max_sec=3.0):
    time.sleep(random.uniform(min_sec, max_sec))

# ===========================
# RANDOM SCROLL
# ===========================

def random_scroll(driver, min_scrolls=2, max_scrolls=5):
    """
    Scrolls randomly to mimic human reading behavior
    """

    # ✅ Step 1: scroll down gradually
    for _ in range(random.randint(2, 5)):
        down_amount = random.randint(300, 900)
        driver.execute_script("window.scrollBy(0, arguments[0]);", down_amount)
        time.sleep(random.uniform(0.4, 1.2))

    # ✅ Step 2: small pause (reading behavior)
    time.sleep(random.uniform(0.8, 2.0))

    # ✅ Step 3: scroll back up slightly (not full reset)
    up_amount = random.randint(200, 600)
    driver.execute_script("window.scrollBy(0, -arguments[0]);", up_amount)

    time.sleep(random.uniform(0.5, 1.2))

    # ✅ Step 4: tiny correction scroll (very human-like)
    micro_adjust = random.randint(-100, 100)
    driver.execute_script("window.scrollBy(0, arguments[0]);", micro_adjust)

   # ✅ Step 3: scroll back to TOP (critical for clickability)
    driver.execute_script("window.scrollTo(0, 0);")

    # ✅ Step 4: small human pause
    time.sleep(random.uniform(0.8, 1.5))

# ===========================
# HUMAN TYPING
# ===========================

def human_typing(element, text, min_delay=0.05, max_delay=0.2):
    """
    Types text character by character like a human
    """
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))


# ===========================
# FIND WITH RETRIES
# ===========================

def find_with_retries(find_func, attempts=3, base_delay=1):
    """
    Retry wrapper for unstable elements
    Example:
        element = find_with_retries(lambda: driver.find_element(...))
    """
    last_exception = None

    for attempt in range(attempts):
        try:
            return find_func()
        except Exception as e:
            last_exception = e
            time.sleep(base_delay * (attempt + 1))

    raise last_exception

# ===========================
# OPTIONAL: RANDOM PAUSE ACTION
# ===========================

def random_action_pause(probability=0.3):
    """
    Sometimes pause randomly to mimic thinking/reading
    """
    if random.random() < probability:
        time.sleep(random.uniform(1, 3))

# ===========================
# Clear Words manually
# ===========================
def clear_words(element):
    element.send_keys(Keys.CONTROL + "a")  # Select all text
    element.send_keys(Keys.DELETE)          # Delete selected text