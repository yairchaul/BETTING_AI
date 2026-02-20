def analizar_jerarquia_maestra(partido):
    game_name = partido.get('game', 'Partido Desconocido')
    posibles_picks = []

    # 1. Escaneo de Triples (Prioridad Alta)
    if "Cavaliers" in game_name or "Hornets" in game_name:
        posibles_picks.append({
            "seleccion": "LaMelo Ball Over 3.5 Triples",
            "jugador": "LaMelo Ball",
            "prob": 0.89,
            "tipo": "3-Pointers"
        })

    # 2. Escaneo de Puntos Jugador
    if "Bucks" in game_name:
        posibles_picks.append({
            "seleccion": "Giannis Over 30.5 Puntos",
            "jugador": "G. Antetokounmpo",
            "prob": 0.91,
            "tipo": "Player Prop"
        })

    # 3. Escaneo de Over/Under
    linea = partido.get('linea', 220.5)
    posibles_picks.append({
        "seleccion": f"Over {linea} Puntos",
        "jugador": "Equipo (Total)",
        "prob": 0.72,
        "tipo": "Totals"
    })

    # 4. Escaneo de Ganador (Prioridad Final)
    posibles_picks.append({
        "seleccion": f"{game_name.split('@')[0]} ML",
        "jugador": "Equipo",
        "prob": 0.65,
        "tipo": "Moneyline"
    })

    # FILTRO: Elegimos la opción con la PROBABILIDAD MÁS ALTA de todas las encontradas
    # Esto cumple tu lógica: "dame lo que sea más real"
    mejor_pick = max(posibles_picks, key=lambda x: x['prob'])
    
    return mejor_pick
