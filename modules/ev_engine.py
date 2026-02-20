def analizar_jerarquia_maestra(partido):
    game_name = partido.get('game', 'Partido Desconocido')
    
    # Simulamos el escaneo simultáneo de los 4 mercados
    # En producción, aquí conectarías con los diccionarios de la API
    opciones = [
        {
            "seleccion": "LaMelo Ball Over 3.5 Triples",
            "protagonista": "LaMelo Ball",
            "prob": 0.89,
            "tipo": "3-Pointers",
            "nota": "🔥 Cavs permiten 12+ triples por juego."
        },
        {
            "seleccion": "Giannis Over 31.5 Puntos",
            "protagonista": "G. Antetokounmpo",
            "prob": 0.92,
            "tipo": "Player Prop",
            "nota": "🎯 Promedio de 34.0 vs Pelicans."
        },
        {
            "seleccion": f"Over {partido.get('linea', 224.5)} Puntos",
            "protagonista": "Global Partido",
            "prob": 0.74,
            "tipo": "Totals",
            "nota": "✅ Ambos equipos en back-to-back."
        },
        {
            "seleccion": f"{game_name.split('@')[0].strip()} ML",
            "protagonista": "Equipo ML",
            "prob": 0.65,
            "tipo": "Moneyline",
            "nota": "⚠️ Cuota con poco valor relativo."
        }
    ]

    # SELECCIÓN JERÁRQUICA: Filtramos por la probabilidad más alta
    # No importa la categoría, el sistema elige lo "más real"
    mejor_pick = max(opciones, key=lambda x: x['prob'])
    
    # Aseguramos que el diccionario de salida sea robusto (Sin Nulos)
    return {
        "game": game_name,
        "label": mejor_pick["seleccion"],
        "sujeto": mejor_pick["protagonista"],
        "confianza": mejor_pick["prob"],
        "categoria": mejor_pick["tipo"],
        "observacion": mejor_pick["nota"]
    }
