def analizar_capas_dinamicas(partido):
    """
    Analiza las 4 capas sin nombres hardcodeados.
    """
    mejor_seleccion = None
    max_prob = 0.0

    # Capas de prioridad
    # Capa 1 y 2: Basadas en la lista real de Selenium
    for m in partido.get('mercados', []):
        # Lógica de probabilidad calculada sobre el momio real
        prob_base = (abs(m['momio']) / (abs(m['momio']) + 100)) if m['momio'] < 0 else (100 / (m['momio'] + 100))
        
        # Bonus por jerarquía: Triples tiene mayor peso estadístico
        peso = 1.2 if "Triples" in m['jugador'] else 1.0
        prob_final = prob_base * peso

        if prob_final > max_prob:
            max_prob = prob_final
            mejor_seleccion = {
                "categoria": "Triples" if "Triples" in m['jugador'] else "Puntos",
                "jugador": m['jugador'],
                "linea": m['linea'],
                "momio": m['momio'],
                "prob": prob_final
            }

    # FILTRO CRÍTICO DEL 70%
    if max_prob < 0.70 or not mejor_seleccion:
        return None

    return {
        "partido": partido['juego'],
        "pick": mejor_seleccion
    }
