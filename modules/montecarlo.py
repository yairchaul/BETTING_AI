import numpy as np

def run_simulations(stats):
    """
    Simulación de Montecarlo para los 13 mercados específicos basados en 
    la media de goles de los últimos 5 partidos.
    """
    # Extraer métricas de los últimos 5 partidos (stats viene de stats_fetch)
    h_avg = stats.get('home_goals_avg', 1.5)
    a_avg = stats.get('away_goals_avg', 1.2)
    
    # Simulamos 10,000 partidos
    sim_home = np.random.poisson(h_avg, 10000)
    sim_away = np.random.poisson(a_avg, 10000)
    total_g = sim_home + sim_away
    
    # Diccionario de resultados (Probabilidades)
    predicciones = {
        # Resultados Finales
        "Resultado Final (Local)": np.mean(sim_home > sim_away),
        "Resultado Final (Empate)": np.mean(sim_home == sim_away),
        "Resultado Final (Visitante)": np.mean(sim_away > sim_home),
        
        # Goles y Ambos Anotan
        "Ambos Equipos Anotan": np.mean((sim_home > 0) & (sim_away > 0)),
        "Over 1.5": np.mean(total_g > 1.5),
        "Over 2.5": np.mean(total_g > 2.5),
        "Over 3.5": np.mean(total_g > 3.5),
        "Under 2.5": np.mean(total_g < 2.5),
        
        # Mercados Combinados (Doble Oportunidad aproximada)
        "Doble Oportunidad (L/E)": np.mean(sim_home >= sim_away),
        "Doble Oportunidad (V/E)": np.mean(sim_away >= sim_home),
        
        # 1ra Mitad (Estimación estadística 45% del total)
        "1ra Mitad Over 0.5": np.mean(np.random.poisson(h_avg * 0.45 + a_avg * 0.45, 10000) > 0.5),
        "1ra Mitad Over 1.5": np.mean(np.random.poisson(h_avg * 0.45 + a_avg * 0.45, 10000) > 1.5),
        "Resultado del partido / Ambos equipos anotan": np.mean((sim_home > sim_away) & (sim_away > 0))
    }
    
    return predicciones
