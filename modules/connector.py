from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def obtener_datos_reales():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") # Indispensable para Streamlit Cloud
    options.add_argument("--disable-dev-shm-usage")

    try:
        # Usa el driver instalado por el sistema (via packages.txt)
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.caliente.mx/sports/en/basketball/nba")
        time.sleep(10) # Mayor tiempo para evitar el error de "mercado no encontrado"
        
        # ... resto de tu lógica de extracción de eventos ...
        return eventos_encontrados
    except Exception as e:
        print(f"Error: {e}")
        return [] # Siempre devuelve lista para evitar errores en el dashboard
    finally:
        if 'driver' in locals(): driver.quit()


# En connector.py (ejemplo con webdriver-manager)


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
