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
    options.add_argument('--window-size=1920,1080')
    # Forzamos el uso de los binarios del sistema instalados en packages.txt
    options.binary_location = "/usr/bin/chromium"
    
    try:
        # En Streamlit Cloud, los binarios se encuentran en estas rutas fijas
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(url)
        # Espera necesaria para que cargue la tabla dinámica de Caliente
        time.sleep(12) 
        
        # Selector robusto para capturar las filas de juegos NBA
        eventos = driver.find_elements(By.CSS_SELECTOR, 'tr.event-row')
        
        data = []
        for ev in eventos:
            try:
                lineas = ev.text.split('\n')
                # Basado en la estructura visual de Caliente
                if len(lineas) >= 5:
                    data.append({
                        "home": lineas[2], # Equipo Local
                        "away": lineas[3], # Equipo Visitante
                        "line": 0.0,
                        "odds_over": lineas[5] if len(lineas) > 5 else "N/A"
                    })
            except Exception:
                continue
                
        driver.quit()
        return data
        
    except Exception as e:
        # Esto te mostrará el error real en tu dashboard para diagnóstico final
        st.error(f"Error crítico de Selenium: {str(e)}")
        return []
