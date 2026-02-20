# modules/ev_engine.py

def buscar_mejor_valor_global(game_data, stats_jugadores):
    """
    Analiza todos los mercados disponibles y devuelve la opción con 
    probabilidad más alta (Safe Pick).
    """
    prob_over = 0.52 # Ejemplo de probabilidad baja para el total
    
    if prob_over < 0.60:
        # Lógica de Pivot: Si el total es dudoso, buscamos rachas de jugadores
        # Aquí es donde vincularemos con APIs de estadísticas reales
        mejor_prop = stats_jugadores.get_top_performer() 
        
        return {
            "mercado": "Player Prop",
            "seleccion": f"{mejor_prop['nombre']} Over {mejor_prop['linea']} Puntos",
            "prob": 0.82, # Alta probabilidad detectada por racha
            "tipo": "Sugerencia de Jugador"
        }
    
    return {"mercado": "Total", "seleccion": "Over", "prob": prob_over, "tipo": "Puntos Partido"}
