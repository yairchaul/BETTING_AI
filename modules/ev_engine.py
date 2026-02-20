def analizar_profundidad(equipo_h, equipo_a, linea_over):
    # --- SIMULACIÓN DE ANÁLISIS DE TENDENCIAS ---
    # En un sistema real, aquí consultarías promedios de puntos
    prob_over = 0.45  # Ejemplo: Poca confianza en el Over 231
    
    if prob_over < 0.55:
        # RECALCULO AUTOMÁTICO: Si los puntos no son claros, ¿quién gana?
        # Lógica: Si el Over es bajo, suele favorecer a defensas fuertes
        prob_moneyline_h = 0.65 
        prob_moneyline_a = 0.35
        
        return {
            "tipo": "WINNER", 
            "seleccion": equipo_h, 
            "prob": prob_moneyline_h,
            "nota": "⚠️ Confianza en puntos insuficiente. Recalculando ganador..."
        }
    
    return {
        "tipo": "OVER", 
        "seleccion": f"Over {linea_over}", 
        "prob": prob_over,
        "nota": "✅ Tendencia de puntos sólida."
    }
