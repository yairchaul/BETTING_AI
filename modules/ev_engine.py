def analizar_jerarquia_maestra(partido):
    # Diccionario de nombres reales para evitar el "None"
    nombres_reales = {
        "CLE@CHA": "Cleveland Cavaliers @ Charlotte Hornets",
        "MIL@NOP": "Milwaukee Bucks @ New Orleans Pelicans",
        "LAC@LAL": "LA Clippers @ LA Lakers"
    }
    
    # Obtenemos el nombre limpio o un genérico válido
    game_id = partido.get('game_id', 'NBA Game')
    game_display = nombres_reales.get(game_id, partido.get('game', 'Partido NBA'))

    # Simulamos la jerarquía de mercados (Elige el de mayor % automáticamente)
    # Prioridad: 1. Triples, 2. Puntos Jugador, 3. Over/Under, 4. Ganador
    mercados = [
        {"sel": "LaMelo Ball Over 3.5 Triples", "prob": 0.89, "tipo": "Triples", "sujeto": "LaMelo Ball"},
        {"sel": "Giannis Over 30.5 Puntos", "prob": 0.91, "tipo": "Puntos", "sujeto": "Giannis A."},
        {"sel": f"Over {partido.get('linea', 222.5)}", "prob": 0.72, "tipo": "Totals", "sujeto": "Equipo"},
        {"sel": f"{game_display.split('@')[0]} ML", "prob": 0.65, "tipo": "Moneyline", "sujeto": "Equipo"}
    ]

    # Retorna solo el de mayor probabilidad
    mejor = max(mercados, key=lambda x: x['prob'])
    return {
        "partido": game_display,
        "seleccion": mejor["sel"],
        "prob": mejor["prob"],
        "jugador": mejor["sujeto"]
    }
