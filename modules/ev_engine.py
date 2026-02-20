def analizar_jerarquia_acumulativa(partido):
    # Aseguramos que el nombre del partido nunca sea None
    game_name = partido.get('game', 'Partido Desconocido')
    posibilidades = []

    # Mercado 1: Triples de Jugador (Alta Especificidad)
    if "Hornets" in game_name:
        posibilidades.append({
            "seleccion": "LaMelo Ball Over 3.5 Triples",
            "jugador": "LaMelo Ball",
            "prob": 0.89,
            "tipo": "3-Pointers"
        })

    # Mercado 2: Puntos de Jugador (Player Props)
    if "Bucks" in game_name:
        posibilidades.append({
            "seleccion": "Giannis Over 30.5 Puntos",
            "jugador": "G. Antetokounmpo",
            "prob": 0.91,
            "tipo": "Player Prop"
        })

    # Mercado 3: Over/Under Total
    linea = partido.get('linea', 222.5)
    posibilidades.append({
        "seleccion": f"Over {linea} Puntos",
        "jugador": "Equipo (Total)",
        "prob": 0.75,
        "tipo": "Totals"
    })

    # Mercado 4: Ganador del Partido (Moneyline)
    posibilidades.append({
        "seleccion": f"{game_name.split('@')[0].strip()} a Ganar",
        "jugador": "Equipo",
        "prob": 0.68,
        "tipo": "Moneyline"
    })

    # 🏆 FILTRO MAESTRO: Selecciona el mercado con la probabilidad más alta
    # Si hay un empate, prioriza el mercado más específico (jugador sobre equipo)
    mejor_pick = max(posibilidades, key=lambda x: x['prob'])
    
    return mejor_pick
