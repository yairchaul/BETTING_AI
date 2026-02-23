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
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Configuración de sigilo para evitar la carga infinita
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.binary_location = "/usr/bin/chromium"
    
    # User-Agent moderno para imitar un navegador real
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

    driver = None
    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        
        # SCRIPT CRÍTICO: Elimina la propiedad 'webdriver' para que no nos detecten como bot
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
          "source": "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        })
        
        driver.get(url)
        
        # Tiempo extendido para superar la pantalla de carga de Caliente
        time.sleep(22) 
        
        # Captura de pantalla actualizada para el bloque de debug
        driver.save_screenshot("debug_screen.png") 
        
        # Selectores actualizados para la tabla de NBA
        eventos = driver.find_elements(By.CSS_SELECTOR, 'tr.event-row, .coupon-row-item')
        
        data = []
        for ev in eventos:
            try:
                lineas = ev.text.split('\n')
                # Filtramos solo si hay datos de equipos y momios
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
        
    except Exception:
        return []
    finally:
        if driver:
            driver.quit()

