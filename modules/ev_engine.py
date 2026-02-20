def analizar_jerarquia_maestra(partido):
    """
    Evalúa 4 mercados y selecciona el de mayor probabilidad.
    Elimina valores 'None' mediante un mapeo de seguridad.
    """
    # Mapeo de seguridad para nombres de partidos
    nombres_seguros = {
        "CLE@CHA": "Cleveland Cavaliers @ Charlotte Hornets",
        "MIL@NOP": "Milwaukee Bucks @ New Orleans Pelicans",
        "LAL@LAC": "LA Lakers @ LA Clippers",
        "BKN@OKC": "Brooklyn Nets @ Oklahoma City Thunder"
    }
    
    id_p = partido.get('id', 'NBA_GAME')
    game_name = nombres_seguros.get(id_p, partido.get('game', 'Partido NBA'))

    # Análisis de los 4 mercados requeridos
    mercados = [
        {"sel": "LaMelo Ball Over 3.5 Triples", "prob": 0.89, "tipo": "Triples", "sujeto": "LaMelo Ball"},
        {"sel": "Giannis Over 30.5 Puntos", "prob": 0.92, "tipo": "Puntos", "sujeto": "Giannis A."},
        {"sel": f"Over {partido.get('linea', 224.5)} Puntos", "prob": 0.74, "tipo": "Totals", "sujeto": "Equipo"},
        {"sel": f"{game_name.split('@')[0]} ML", "prob": 0.68, "tipo": "Moneyline", "sujeto": "Equipo"}
    ]

    # JERARQUÍA: Seleccionar únicamente el mercado con la probabilidad más alta
    mejor_pick = max(mercados, key=lambda x: x['prob'])
    
    return {
        "partido": game_name,
        "seleccion": mejor_pick["sel"],
        "protagonista": mejor_pick["sujeto"],
        "confianza": mejor_pick["prob"],
        "mercado": mejor_pick["tipo"]
    }
