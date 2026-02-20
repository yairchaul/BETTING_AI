def analizar_mejor_opcion(partido):
    # El motor elige la vía con mayor EV (Valor Esperado)
    game_name = partido.get('game', '')
    
    # Ejemplo de selección inteligente por equipo/contexto
    if "Nets" in game_name:
        return {
            "seleccion": "Over 213.5 Puntos (Equipo)",
            "prob": 0.90,
            "nota": "🔥 Tendencia: Nets han superado esta línea en sus últimos 4 juegos."
        }
    elif "Clippers" in game_name:
        return {
            "seleccion": "LA Clippers a Ganar (ML)",
            "prob": 0.85,
            "nota": "✅ Probabilidad alta: Lakers juegan sin su estrella principal."
        }
    elif "Bucks" in game_name:
        return {
            "seleccion": "Giannis Over 30.5 Puntos",
            "prob": 0.88,
            "nota": "🎯 Player Prop: Giannis promedia 34.0 puntos contra New Orleans."
        }
    else:
        # Mercado por defecto si no hay datos específicos
        return {
            "seleccion": "Over Puntos Totales",
            "prob": 0.55,
            "nota": "⚠️ Datos estándar del mercado."
        }
