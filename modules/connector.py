# modules/connector.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import streamlit as st

def get_live_data(url='https://www.caliente.mx/sports/es_MX/basketball/NBA'):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    # Forzamos la ruta del binario instalado vía packages.txt
    options.binary_location = "/usr/bin/chromium"
    
    # IMPORTANTE: Definimos la ruta del driver del sistema explícitamente
    webdriver_service = Service("/usr/bin/chromedriver")

    try:
        driver = webdriver.Chrome(service=webdriver_service, options=options)
        driver.get(url)
        
        # Tiempo extendido para que la tabla de momios cargue
        time.sleep(12) 
        
        # Buscamos las filas de eventos NBA
        eventos = driver.find_elements(By.CSS_SELECTOR, 'tr.event-row, .coupon-row')
        
        data = []
        for ev in eventos:
            try:
                # Extraemos el texto de la fila (ej. "San Antonio Spurs", "Detroit Pistons")
                detalles = ev.text.split('\n')
                if len(detalles) > 5:
                    data.append({
                        "home": detalles[2],  # Equipo 1
                        "away": detalles[3],  # Equipo 2
                        "line": 0.0,
                        "odds_over": detalles[5] if len(detalles) > 5 else "-110"
                    })
            except:
                continue
        
        driver.quit()
        return data
    except Exception as e:
        # Esto nos dirá exactamente qué falta en la nube
        st.error(f"Fallo técnico: {str(e)}")
        return []

