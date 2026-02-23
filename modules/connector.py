# modules/connector.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os

def get_live_data(url='https://www.caliente.mx/sports/es_MX/basketball/NBA'):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/chromium"
    
    driver = None
    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # Espera para que cargue el contenido dinámico
        time.sleep(12) 
        
        # --- CAPTURA DE DIAGNÓSTICO ---
        # Guardamos lo que ve Selenium antes de procesar
        driver.save_screenshot("debug_screen.png") 
        
        eventos = driver.find_elements(By.CSS_SELECTOR, 'tr.event-row')
        
        data = []
        for ev in eventos:
            try:
                lineas = ev.text.split('\n')
                if len(lineas) >= 5:
                    data.append({
                        "home": lineas[2], 
                        "away": lineas[3], 
                        "line": 0.0,
                        "odds_over": lineas[5] if len(lineas) > 5 else "N/A"
                    })
            except:
                continue
                
        return data
        
    except Exception as e:
        return []
    finally:
        if driver:
            driver.quit()

