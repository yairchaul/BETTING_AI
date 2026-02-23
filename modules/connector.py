# modules/connector.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import logging
import time

logging.basicConfig(level=logging.INFO)

def get_live_data(url='https://caliente.mx/deportes/basquetbol/nba'):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    driver = None
    try:
        logging.info("Iniciando navegador...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        driver.get(url)
        
        # Espera más larga + scroll para cargar JS lazy
        time.sleep(8)  # Dar tiempo a que cargue el DOM dinámico
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        wait = WebDriverWait(driver, 30)
        
        # Selectores alternativos más robustos (probados en sitios similares)
        selectors = [
            (By.CSS_SELECTOR, '[data-testid="bet-event"], .bet-event, .event-row, .match-row'),
            (By.XPATH, "//div[contains(@class, 'event') or contains(@class, 'match') or contains(@class, 'game')]"),
            (By.CSS_SELECTOR, '.player-prop, .prop-row, [data-type*="player"], .odds-container')
        ]

        data = []
        elementos_encontrados = False
        
        for by, selector in selectors:
            try:
                wait.until(EC.presence_of_element_located((by, selector)))
                elementos = driver.find_elements(by, selector)
                if elementos:
                    logging.info(f"Encontrados {len(elementos)} elementos con selector: {selector}")
                    elementos_encontrados = True
                    for elem in elementos[:10]:  # Limitar para debug
                        try:
                            # Intentar extraer datos genéricos
                            texto = elem.text.strip()
                            if texto:
                                data.append({
                                    'raw_text': texto,
                                    'match': 'Pendiente parseo',
                                    'player': 'Pendiente',
                                    'type': 'unknown',
                                    'line': 0.0,
                                    'odds_over': 'N/A'
                                })
                        except:
                            continue
                    break
            except TimeoutException:
                logging.warning(f"Selector {selector} no encontró elementos")
                continue

        if not elementos_encontrados:
            logging.error("Ningún selector funcionó. Posible cambio en estructura del sitio.")
            # Screenshot para debug (opcional, guarda en /tmp)
            try:
                driver.save_screenshot('/tmp/caliente_debug.png')
                logging.info("Screenshot guardado en /tmp/caliente_debug.png")
            except:
                pass

        return data if data else []

    except Exception as e:
        logging.error(f"Error grave en Selenium: {e}")
        return []
    finally:
        if driver:
            driver.quit()
