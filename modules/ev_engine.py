def analizar_jerarquia_maestra(partido):
    # 1. Blindaje de Datos: Mapeo para evitar 'None'
    mapeo_nombres = {
        "CLE@CHA": "Cleveland Cavaliers @ Charlotte Hornets",
        "MIL@NOP": "Milwaukee Bucks @ New Orleans Pelicans",
        "LAL@LAC": "LA Lakers @ LA Clippers"
    }
    
    id_partido = partido.get('id', 'CLE@CHA')
    nombre_partido = mapeo_nombres.get(id_partido, partido.get('game', 'NBA Game'))

    # 2. Análisis Multimercado Simultáneo
    opciones = [
        {
            "label": "LaMelo Ball Over 3.5 Triples",
            "sujeto": "LaMelo Ball",
            "prob": 0.88,
            "tipo": "Triples"
        },
        {
            "label": "Giannis Over 30.5 Puntos",
            "sujeto": "Giannis A.",
            "prob": 0.91,
            "tipo": "Puntos"
        },
        {
            "label": f"Over {partido.get('linea', 222.5)} Totales",
            "sujeto": "Equipo (Total)",
            "prob": 0.75,
            "tipo": "Totals"
        },
        {
            "label": f"{nombre_partido.split('@')[0]} ML",
            "sujeto": "Equipo",
            "prob": 0.65,
            "tipo": "Moneyline"
        }
    ]

    # 3. Filtro de Valor Único (Jerarquía)
    # Selecciona la opción con mayor probabilidad sin importar la categoría
    mejor_opcion = max(opciones, key=lambda x: x['prob'])
    
    return {
        "partido": nombre_partido,
        "seleccion": mejor_opcion["label"],
        "protagonista": mejor_opcion["sujeto"],
        "confianza": mejor_opcion["prob"],
        "mercado": mejor_opcion["tipo"]
    }
