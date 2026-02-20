from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def obtener_datos_reales():
    """
    Escanea Caliente.mx dinámicamente. Extrae jugadores reales como los de la imagen.
    """
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox") # Necesario para servidores Linux (Streamlit Cloud)
    options.add_argument("--disable-dev-shm-usage") # Evita errores de memoria

    # BLINDAJE 1: Uso de Service y WebDriver Manager para evitar fallos de ruta
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get("https://www.caliente.mx/sports/en/basketball/nba")
        time.sleep(8) # Aumentamos a 8s para asegurar la carga en el servidor

        eventos = driver.find_elements(By.CLASS_NAME, "event-card") 
        partidos_en_vivo = []
        
        for ev in eventos:
            try:
                nombre_juego = ev.find_element(By.CLASS_NAME, "event-name").text
                secciones_jugadores = ev.find_elements(By.CLASS_NAME, "market-selection")
                mercados_reales = []
                
                for s in secciones_jugadores:
                    datos = s.text.split('\n') 
                    # BLINDAJE 2: Validación robusta de la estructura del mercado
                    if len(datos) >= 3:
                        mercados_reales.append({
                            "jugador": datos[0], # Ej: Zion Williamson
                            "linea": datos[1],   # Ej: Over (23.5)
                            "momio": datos[2]    # Ej: -120
                        })
                
                if mercados_reales:
                    partidos_en_vivo.append({
                        "juego": nombre_juego,
                        "mercados": mercados_reales
                    })
            except:
                continue # Si un partido falla, sigue con el siguiente
                
        return partidos_en_vivo
        
    except Exception as e:
        print(f"Error Crítico en Selenium: {e}")
        return [] # BLINDAJE 3: Siempre devuelve lista vacía si falla para no romper el dashboard
    finally:
        if 'driver' in locals():
            driver.quit()
