from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

logging.basicConfig(level=logging.ERROR)

def get_live_data(url='https://caliente.mx/deportes/basquetbol/nba'):
    options = Options()
    options.add_argument('--headless=new')  # Nueva opción headless más estable
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')  # Evita detección bot

    try:
        # webdriver-manager descarga/instala chromedriver compatible automáticamente
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bet-event')))  # Tu selector
        
        # ... tu scraping aquí ...
        data = []  # parsea elementos
        # Ejemplo placeholder
        events = driver.find_elements(By.CSS_SELECTOR, '.bet-event')
        # ... procesa ...

        return data if data else []
    except (TimeoutException, WebDriverException, Exception) as e:
        logging.error(f"Selenium falló: {e}")
        return []
    finally:
        if 'driver' in locals():
            driver.quit()

