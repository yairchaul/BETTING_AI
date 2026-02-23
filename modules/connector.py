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
    # Evita que el sitio detecte que es una automatización
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    options.binary_location = "/usr/bin/chromium"
    
    # User-agent más realista para evitar la pantalla de carga infinita
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

    driver = None
    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        
        # Inyectamos script para ocultar rastros de Selenium
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
          "source": "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        })
        
        driver.get(url)
        
        # Aumentamos el tiempo a 20 segundos para que pase la pantalla de carga
        time.sleep(20) 
        
        # Tomamos captura para verificar si ya cargó la tabla
        driver.save_screenshot("debug_screen.png") 
        
        # Intentamos capturar los juegos reales
        eventos = driver.find_elements(By.CSS_SELECTOR, 'tr.event-row, .coupon-row-item')
        
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

