# modules/connector.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_live_data():
    # URL directa a la sección de NBA para evitar pasos extra
    url = 'https://www.caliente.mx/sports/es_MX/basketball/NBA'
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    
    # 1. MÁSCARA DE NAVEGADOR REAL: Evita que el sitio sepa que es un bot
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    options.binary_location = "/usr/bin/chromium"
    
    driver = None
    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        
        # 2. BORRADO DE HUELLAS: Script para ocultar Selenium
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
          "source": "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        })
        
        driver.get(url)
        
        # 3. ESPERA DINÁMICA: Esperamos hasta 30 segundos a que aparezca la tabla de juegos
        # Esto es mejor que un time.sleep fijo porque detecta cuando la carga termina
        wait = WebDriverWait(driver, 30)
        
        try:
            # Esperamos a que aparezca cualquier fila de la tabla de NBA
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'event-row')))
        except:
            # Si falla, tomamos captura para ver qué pasó tras la espera
            driver.save_screenshot("debug_screen.png")
            return []

        # 4. CAPTURA FINAL DE ÉXITO
        driver.save_screenshot("debug_screen.png")
        
        eventos = driver.find_elements(By.CLASS_NAME, 'event-row')
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
        
    except Exception:
        return []
    finally:
        if driver:
            driver.quit()

