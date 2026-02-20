def analizar_profundidad_maestra(partido):
    # Validamos datos para evitar KeyError
    game_name = partido.get('game', 'Partido Desconocido')
    posibilidades = []

    # --- CAPA 1: PUNTOS DE JUGADOR (PLAYER PROPS) ---
    if "Bucks" in game_name:
        posibilidades.append({"sel": "Giannis Over 30.5 Pts", "prob": 0.91, "tipo": "Player Prop", "jug": "Giannis A."})
    
    # --- CAPA 2: TRIPLES (Basado en tu imagen de Caliente) ---
    if "Hornets" in game_name or "Cavaliers" in game_name:
        # Aquí sumamos la detección de LaMelo que vimos en la captura
        posibilidades.append({"sel": "LaMelo Ball Over 3.5 Triples", "prob": 0.88, "tipo": "3-Pointers", "jug": "LaMelo Ball"})

    # --- CAPA 3: GANADOR DIRECTO (MONEYLINE) ---
    if "Clippers" in game_name:
        posibilidades.append({"sel": "Clippers a Ganar", "prob": 0.84, "tipo": "Moneyline", "jug": "Equipo"})

    # --- CAPA 4: TOTALES (OVER/UNDER) ---
    linea_o_u = partido.get('linea', 225.5)
    posibilidades.append({"sel": f"Over {linea_o_u}", "prob": 0.65, "tipo": "Totals", "jug": "Equipo (Total)"})

    # 🔥 FILTRO MAESTRO: Seleccionamos la opción con mayor probabilidad de todas las anteriores
    # Esto asegura que no eliminamos nada, solo elegimos lo mejor
    mejor_opcion = max(posibilidades, key=lambda x: x['prob'])
    
    return mejor_opcion
