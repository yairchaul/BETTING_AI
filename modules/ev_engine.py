def limpiar_nombre_partido(partido):
    # BLINDAJE ANTI-NONE: Reconstruye el nombre si viene vacío
    game_name = partido.get('game')
    if not game_name or game_name == "None":
        id_partido = partido.get('id', 'NBA@GAME')
        if '@' in id_partido:
            visitante, local = id_partido.split('@')
            game_name = f"{visitante} vs {local}"
        else:
            game_name = "NBA Matchup"
    return game_name

def analizar_jerarquia_por_partido(partido):
    game_name = limpiar_nombre_partido(partido)
    
    # REPOSITORIO DE CAPAS (Se evalúan simultáneamente)
    capas = []

    # CAPA 1: Triples (Prioridad 1)
    capas.append({
        "label": "Over 3.5 Triples",
        "sujeto": "Jugador Estrella",
        "prob": 0.85 + (0.10 * (partido.get('id', 'A')[0] > 'M')), # Simulación lógica
        "mercado": "Triples"
    })

    # CAPA 2: Puntos Jugador (Prioridad 2)
    capas.append({
        "label": "Over 24.5 Puntos",
        "sujeto": "Líder Anotador",
        "prob": 0.78,
        "mercado": "Player Props"
    })

    # CAPA 3: Over/Under Partido (Prioridad 3)
    capas.append({
        "label": f"Over {partido.get('linea', 222.5)} Totales",
        "sujeto": "Equipo",
        "prob": 0.72,
        "mercado": "Totals"
    })

    # CAPA 4: Ganador / ML (Prioridad 4)
    capas.append({
        "label": "Victoria Directa (ML)",
        "sujeto": "Equipo Favorito",
        "prob": 0.65,
        "mercado": "Moneyline"
    })

    # FILTRO DE ÉLITE: Elegir solo la capa con mayor probabilidad
    mejor_mercado = max(capas, key=lambda x: x['prob'])

    return {
        "partido": game_name,
        "seleccion": mejor_mercado["label"],
        "protagonista": mejor_mercado["sujeto"],
        "confianza": mejor_mercado["prob"],
        "categoria": mejor_mercado["mercado"]
    }
