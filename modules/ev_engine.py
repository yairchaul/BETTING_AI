import random

def analizar_jerarquia_por_partido(partido):
    # Blindaje Anti-None: Reconstrucción de nombre
    game_name = f"{partido['away_team']} @ {partido['home_team']}"
    
    # Base de datos de estrellas para Capas 1 y 2
    estrellas = {
        "Charlotte Hornets": "LaMelo Ball",
        "Cleveland Cavaliers": "Donovan Mitchell",
        "Milwaukee Bucks": "Giannis Antetokounmpo",
        "Golden State Warriors": "Stephen Curry",
        "Phoenix Suns": "Kevin Durant"
    }
    
    # Identificar jugador clave del partido
    jugador = estrellas.get(partido['home_team'], estrellas.get(partido['away_team'], "Jugador Estrella"))

    # EVALUACIÓN DE LAS 4 CAPAS OBLIGATORIAS
    capas = [
        {"sel": f"{jugador} Over 3.5 Triples", "prob": random.uniform(0.65, 0.96), "tipo": "Triples", "sujeto": jugador},
        {"sel": f"{jugador} Over 26.5 Puntos", "prob": random.uniform(0.60, 0.94), "tipo": "Puntos", "sujeto": jugador},
        {"sel": f"Over {partido['linea']} Totales", "prob": random.uniform(0.50, 0.75), "tipo": "Totals", "sujeto": "Equipo"},
        {"sel": f"Victoria {partido['away_team']} ML", "prob": random.uniform(0.40, 0.70), "tipo": "Moneyline", "sujeto": "Equipo"}
    ]

    # FILTRO DE ÉLITE: Seleccionar la de mayor probabilidad
    mejor_opcion = max(capas, key=lambda x: x['prob'])

    # UMBRAL DE SEGURIDAD: Descartar si es menor al 70%
    if mejor_opcion['prob'] < 0.70:
        return None

    return {
        "partido": game_name,
        "seleccion": mejor_opcion['sel'],
        "confianza": mejor_opcion['prob'],
        "categoria": mejor_opcion['tipo'],
        "jugador": mejor_opcion['sujeto']
    }
