# modules/autopicks.py
from modules.connector import get_live_data

def generar_picks_auto():
    """
    Extrae datos reales de Caliente.mx y genera sugerencias automáticas.
    """
    datos_vivos = get_live_data()
    
    if not datos_vivos:
        return ["Esperando datos reales de Caliente.mx..."]
    
    # Genera la lista basada en lo que Selenium encontró en la pantalla
    picks_reales = []
    for juego in datos_vivos:
        jugador = juego.get('player', 'Jugador Desconocido')
        linea = juego.get('line', '0.0')
        picks_reales.append(f"{jugador} Over {linea}")
        
    return picks_reales
