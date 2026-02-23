# modules/autopicks.py
from modules.connector import get_live_data

def generar_picks_auto():
    """
    Toma la información viva y la presenta como sugerencias de apuesta.
    """
    datos = get_live_data()
    
    if not datos:
        return ["Sin mercados detectados en este momento. Intenta en unos minutos."]
    
    # Transformamos los datos del conector en frases legibles
    sugerencias = []
    for d in datos:
        sugerencias.append(f"🔥 {d['player']} | Línea: {d['line']} | Momio: {d['odds_over']}")
    
    return sugerencias
