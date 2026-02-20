def analizar_jerarquia_maestra(partido_raw):
    # Ya no hay nombres manuales, usamos lo que Selenium leyó
    candidatos = []
    
    for prop in partido_raw.get('player_props', []):
        # El análisis se basa en la jerarquía (Triples > Puntos)
        peso = 1.3 if "Triples" in prop['original'] else 1.1
        probabilidad = (0.55 * peso) # Simulación de probabilidad real
        
        candidatos.append({
            "seleccion": prop['original'],
            "prob": probabilidad,
            "momio": prop['momio'],
            "tipo": "Prop de Jugador"
        })

    if not candidatos:
        return None

    # ELEGIR EL MEJOR (FILTRO DE ÉLITE)
    mejor_opcion = max(candidatos, key=lambda x: x['prob'])
    
    # FILTRO DE SEGURIDAD (70%)
    if mejor_opcion['prob'] < 0.70:
        return None

    return {
        "partido": partido_raw['name'],
        "pick": mejor_opcion
    }
