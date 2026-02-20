def analizar_jerarquia_por_partido(partido):
    import random
    
    # 1. Capas de mercado con probabilidades dinámicas
    # Usamos random solo para simular el análisis de la API en este ejemplo
    capas = [
        {"sel": "Over 3.5 Triples", "prob": random.uniform(0.6, 0.95), "tipo": "Triples"},
        {"sel": "Over 26.5 Puntos", "prob": random.uniform(0.6, 0.92), "tipo": "Puntos"},
        {"sel": f"Over {partido['linea']} Totales", "prob": 0.65, "tipo": "Totals"}, # Prob baja fija para test
        {"sel": "Victoria ML", "prob": 0.68, "tipo": "Moneyline"}
    ]

    # 2. Selección del mejor del partido
    mejor_del_partido = max(capas, key=lambda x: x['prob'])

    # 3. FILTRO CRÍTICO: Si la probabilidad es menor al 70%, se descarta el partido
    if mejor_del_partido['prob'] < 0.70:
        return None 

    return {
        "partido": partido['game'],
        "seleccion": mejor_del_partido['sel'],
        "confianza": mejor_del_partido['prob'],
        "categoria": mejor_mercado['tipo']
    }
