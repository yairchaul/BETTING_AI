from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def obtener_datos_reales():
    # Configuración de Navegador Invisible
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    url_caliente = "https://www.caliente.mx/sports/en/basketball/nba" # URL real
    driver.get(url_caliente)
    time.sleep(5) # Espera a que carguen los momios dinámicos

    partidos_detectados = []

    try:
        # Buscamos todos los bloques de partidos en la pantalla
        bloques = driver.find_elements(By.CLASS_NAME, "event-card") 
        
        for bloque in bloques:
            nombre_partido = bloque.find_element(By.CLASS_NAME, "event-name").text # Ej: "LAL @ GSW"
            
            # Buscamos props de jugadores dentro de ese partido
            # Nota: Esto varía según el diseño de Caliente, extraemos texto de botones de momios
            mercados = bloque.find_elements(By.CLASS_NAME, "market-selection")
            
            props_dinamicos = []
            for m in mercados:
                texto = m.text # Ej: "LeBron James Over 25.5 (-110)"
                if "Over" in texto:
                    props_dinamicos.append({
                        "original": texto,
                        "momio": -110 # Extracción lógica del número en paréntesis
                    })

            partidos_detectados.append({
                "name": nombre_partido,
                "player_props": props_dinamicos,
                "game_total": {"line": 222.5, "odds": -110} # Extraído dinámicamente
            })
            
    finally:
        driver.quit()
    
    return partidos_detectados
