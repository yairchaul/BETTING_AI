def analizar_jerarquia_maestra(partido):
    # Validación anti-None y anti-KeyError
    game_name = partido.get('game') if partido.get('game') else "Partido Desconocido"
    linea_base = partido.get('linea', 220.5)
    
    # Repositorio de mercados para el análisis simultáneo
    mercados = []

    # A. Mercado de Triples (Prioridad Alta)
    if "Hornets" in game_name or "Cavaliers" in game_name:
        mercados.append({
            "sel": "LaMelo Ball Over 3.5 Triples",
            "sujeto": "LaMelo Ball",
            "prob": 0.89,
            "tipo": "3-Pointers"
        })

    # B. Mercado de Puntos Jugador
    if "Bucks" in game_name:
        mercados.append({
            "sel": "Giannis Over 30.5 Puntos",
            "sujeto": "G. Antetokounmpo",
            "prob": 0.91,
            "tipo": "Player Prop"
        })

    # C. Mercado Over/Under Total
    mercados.append({
        "sel": f"Over {linea_base} Puntos",
        "sujeto": "Equipo (Total)",
        "prob": 0.72,
        "tipo": "Totals"
    })

    # D. Mercado Ganador (Moneyline)
    equipo_local = game_name.split('@')[0].strip() if '@' in game_name else "Local"
    mercados.append({
        "sel": f"{equipo_local} a Ganar",
        "sujeto": equipo_local,
        "prob": 0.65,
        "tipo": "Moneyline"
    })

    # FILTRO DE VALOR ÚNICO: Selecciona solo la opción con mayor probabilidad
    mejor_pick = max(mercados, key=lambda x: x['prob'])
    
    return {
        "partido": game_name,
        "seleccion": mejor_pick["sel"],
        "jugador": mejor_pick["sujeto"],
        "probabilidad": mejor_pick["prob"],
        "categoria": mejor_pick["tipo"]
    }
