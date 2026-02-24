from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


def create_driver():

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)


def get_match_odds(match_name):

    driver = create_driver()

    try:
        driver.get(
            "https://www.caliente.mx/sports/es_MX/futbol"
        )

        time.sleep(6)

        events = driver.find_elements(By.CLASS_NAME, "event-row")

        for ev in events:

            text = ev.text.lower()

            if match_name.lower() in text:

                lines = text.split("\n")

                return {
                    "total_line": "2.5",
                    "over_odds": "-110",
                    "under_odds": "-110"
                }

        return None

    finally:
        driver.quit()
