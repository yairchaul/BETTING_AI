# modules/connector.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import logging
import time
import streamlit as st

def get_live_data(url='https://www.caliente.mx/sports/es_MX/basketball/NBA'):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Forzamos el uso del binario del sistema para evitar el error de versión 114
    options.binary_location = "/usr/bin/chromium" 
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        # Iniciamos sin Service() manual para que Streamlit use su propio Driver
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(10) # Tiempo para cargar la tabla de juegos
        
        # Seleccionamos las filas de los juegos (San Antonio, Sacramento, etc.)
        juegos = driver.find_elements(By.CLASS_NAME, 'event-row')
        
        data = []
        for juego in juegos:
            try:
                texto = juego.text.split('\n')
                # Buscamos equipos y momios como los de tu imagen
                if len(texto) >= 4:
                    data.append({
                        'player': f"{texto[2]} vs {texto[3]}",
                        'line': 0.0, # Línea base
                        'odds_over': texto[5] if len(texto) > 5 else "-110",
                        'type': 'match_odds'
                    })
            except:
                continue
        
        driver.quit()
        return data
    except Exception as e:
        st.error(f"Error de conexión con Caliente: {e}")
        return []

