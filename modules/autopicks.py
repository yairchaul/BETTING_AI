# modules/autopicks.py
from modules.connector import get_live_data

def generar_picks_auto():
    """
    Transforma los datos de Caliente en sugerencias reales.
    """
    datos = get_live_data()
    
    if not datos:
        return ["No se detectaron juegos. Revisa si hay partidos en vivo en Caliente.mx."]
    
    # Crea la lista basada en los equipos reales encontrados
    return [f"🏀 {d['player']} | Odds: {d['odds_over']}" for d in datos]
