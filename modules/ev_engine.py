def analizar_mejor_opcion(partido):
    # Simulamos consulta a racha (NBA Stats)
    # En una versión pro, aquí llamarías a una API de estadísticas de jugadores
    
    prob_over = 0.55
    prob_ganador_home = 0.62
    prob_player_prop = 0.85 # Ejemplo: Racha de 5 partidos cumpliendo
    
    # El sistema elige la opción con mayor EV (Valor Esperado)
    if prob_player_prop > 0.80:
        return {
            "seleccion": "Donovan Mitchell Over 25.5 Pts",
            "prob": prob_player_prop,
            "tipo": "PLAYER PROP",
            "nota": "🔥 Racha detectada: Superó la línea en 4 de últimos 5."
        }
    elif prob_ganador_home > 0.70:
        return {
            "seleccion": f"Ganador {partido['home']}",
            "prob": prob_ganador_home,
            "tipo": "MONEYLINE",
            "nota": "✅ Ventaja clara de localía."
        }
    else:
        return {
            "seleccion": f"Over {partido.get('linea', 0)}",
            "prob": prob_over,
            "tipo": "TOTALS",
            "nota": "⚠️ Confianza media en puntos."
        }
