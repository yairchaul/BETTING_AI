# modules/connector.py

import streamlit as st
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================================================
# 🔐 OBTENER API KEY SEGURA
# =========================================================
def get_api_key():
    """
    Prioridad:
    1. Streamlit Cloud Secrets
    2. Variable de entorno local
    """
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return os.getenv("OPENAI_API_KEY")


# =========================================================
# 🤖 CONFIGURAR DRIVER ANTI-BOT
# =========================================================
def create_driver():

    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # Anti detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )

    options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)

    # Ocultar Selenium
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            const newProto = navigator.__proto__;
            delete newProto.webdriver;
            navigator.__proto__ = newProto;
            """
        },
    )

    return driver


# =========================================================
# 📡 SCRAPER NBA CALIENTE
# =========================================================
def get_live_data():

    url = "https://www.caliente.mx/sports/es_MX/basketball/NBA"

    driver = None

    try:
        driver = create_driver()
        driver.get(url)

        wait = WebDriverWait(driver, 30)

        # esperar eventos
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "event-row"))
        )

        driver.save_screenshot("debug_screen.png")

        eventos = driver.find_elements(By.CLASS_NAME, "event-row")

        data = []

        for ev in eventos:
            try:
                lineas = ev.text.split("\n")

                if len(lineas) >= 5:
                    data.append(
                        {
                            "home": lineas[2],
                            "away": lineas[3],
                            "line": 0.0,
                            "odds_over": lineas[5] if len(lineas) > 5 else "N/A",
                        }
                    )
            except:
                continue

        return data

    except Exception as e:
        print("ERROR SCRAPER:", e)
        return []

    finally:
        if driver:
            driver.quit()


# =========================================================
# 🧪 TEST RÁPIDO
# =========================================================
def test_connection():
    key = get_api_key()

    if key:
        return "✅ API Key detectada"
    else:
        return "❌ API Key NO encontrada"

