from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def obtener_datos_reales():
    """
    Escanea Caliente.mx dinámicamente. No contiene nombres fijos.
    """
    options = Options()
    options.add_argument("--headless") # Navegador invisible
    driver = webdriver.Chrome(options=options)
    
    partidos_en_vivo = []
    try:
        # URL específica de NBA en Caliente
        driver.get("https://www.caliente.mx/sports/en/basketball/nba")
        time.sleep(5) # Espera técnica para carga de scripts dinámicos

        # Localización de tarjetas de eventos
        eventos = driver.find_elements(By.CLASS_NAME, "event-card") 
        
        for ev in eventos:
            nombre_juego = ev.find_element(By.CLASS_NAME, "event-name").text # Ej: MIL @ NOP
            
            # Extraemos la lista de jugadores disponibles en ese momento
            secciones_jugadores = ev.find_elements(By.CLASS_NAME, "market-selection")
            mercados_reales = []
            
            for s in secciones_jugadores:
                # El texto extraído es: "Zion Williamson Over 23.5 (-120)"
                datos = s.text.split('\n') 
                if len(datos) >= 3:
                    mercados_reales.append({
                        "jugador": datos[0],
                        "linea": datos[1],
                        "momio": int(datos[2]) if datos[2] else 0
                    })
            
            partidos_en_vivo.append({
                "juego": nombre_juego,
                "mercados": mercados_reales
            })
            
    except Exception as e:
        print(f"Error en Selenium: {e}")
    finally:
        driver.quit()
        
    return partidos_en_vivo # Blindaje: Siempre devuelve una lista
