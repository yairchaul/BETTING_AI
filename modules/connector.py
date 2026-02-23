# modules/connector.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = None
    try:
        logging.info("Iniciando escáner en vivo...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        driver.get(url)
        
        # Espera a que el contenido dinámico de Caliente cargue
        time.sleep(10) 
        driver.execute_script("window.scrollTo(0, 500);")
        
        wait = WebDriverWait(driver, 20)
        
        # SELECTORES ESPECÍFICOS DE CALIENTE
        # Buscamos los contenedores de apuestas (clase común en Caliente para props)
        market_rows = driver.find_elements(By.CSS_SELECTOR, '.market-table, .mkt-p6, .mkt-group')

        data = []
        logging.info(f"Analizando {len(market_rows)} bloques de mercados encontrados.")

        for row in market_rows:
            try:
                # Extraer texto total del bloque para identificar jugadores
                raw_text = row.text.strip()
                if not raw_text: continue

                # Lógica de extracción por líneas
                # Caliente suele estructurar: JUGADOR | LÍNEA | MOMIO
                lines = raw_text.split('\n')
                
                # Buscamos patrones de Player Props (Jugador + Número de línea)
                for i in range(len(lines)):
                    if any(char.isdigit() for char in lines[i]) and '.' in lines[i]:
                        # Si encontramos una línea (ej. 22.5), el nombre suele estar arriba
                        jugador = lines[i-1] if i > 0 else "Desconocido"
                        linea_val = lines[i].replace('+', '').replace('-', '')
                        momio = lines[i+1] if (i+1) < len(lines) else "N/A"

                        # Limpieza básica para asegurar que sea un Player Prop
                        if len(jugador) > 3 and len(jugador) < 30:
                            data.append({
                                'player': jugador,
                                'match': 'NBA Game Live',
                                'type': 'points/triples',
                                'line': float(linea_val),
                                'odds_over': momio,
                                'raw_text': raw_text[:50] # Solo para debug
                            })
            except:
                continue

        # Si no encontró nada con la lógica anterior, intentar selector de respaldo
        if not data:
            logging.warning("Intentando selector de respaldo para selecciones individuales...")
            selections = driver.find_elements(By.CLASS_NAME, 'sel-nm')
            for sel in selections:
                if sel.text:
                    data.append({'player': sel.text, 'line': 0.0, 'odds_over': 'N/A', 'type': 'raw_extract'})

        logging.info(f"Escaneo finalizado. Picks reales detectados: {len(data)}")
        return data

    except Exception as e:
        logging.error(f"Error grave en Selenium: {e}")
        st.error(f"Fallo en la conexión en vivo: {e}")
        return []
    finally:
        if driver:
            driver.quit()

