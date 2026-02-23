# modules/connector.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import streamlit as st

logging.basicConfig(level=logging.INFO)

def get_live_data(url='https://www.caliente.mx/sports/es_MX/basketball/NBA'):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    # Ruta estándar de Chromium en Streamlit Cloud para evitar el error de versión
    options.binary_location = "/usr/bin/chromium" 
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = None
    try:
        logging.info("Iniciando escáner compatible con el servidor...")
        # Eliminamos Service() y ChromeDriverManager() para evitar conflictos de versión
        driver = webdriver.Chrome(options=options) 
        driver.set_page_load_timeout(60)
        driver.get(url)
        
        # Tiempo para carga de JavaScript dinámico
        time.sleep(10) 
        driver.execute_script("window.scrollTo(0, 500);")
        
        wait = WebDriverWait(driver, 20)
        
        # Localización de mercados reales en Caliente
        market_rows = driver.find_elements(By.CSS_SELECTOR, '.market-table, .mkt-p6, .mkt-group')

        data = []
        for row in market_rows:
            try:
                raw_text = row.text.strip()
                if not raw_text: continue

                lines = raw_text.split('\n')
                for i in range(len(lines)):
                    # Detectar líneas de puntos (ej. 22.5)
                    if any(char.isdigit() for char in lines[i]) and '.' in lines[i]:
                        jugador = lines[i-1] if i > 0 else "Desconocido"
                        linea_val = lines[i].replace('+', '').replace('-', '')
                        momio = lines[i+1] if (i+1) < len(lines) else "N/A"

                        if 3 < len(jugador) < 30:
                            data.append({
                                'player': jugador,
                                'line': float(linea_val),
                                'odds_over': momio,
                                'type': 'points'
                            })
            except:
                continue

        return data

    except Exception as e:
        logging.error(f"Error en Selenium: {e}")
        st.error(f"Fallo en la conexión en vivo: {e}")
        return []
    finally:
        if driver:
            driver.quit()
