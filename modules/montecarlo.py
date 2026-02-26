import numpy as np

def run_simulations(stats):
    """
    Simulación exhaustiva de los 13 mercados solicitados.
    Basado en el análisis de tendencia de los últimos 5 partidos.
    """
    h_avg = stats.get('home_goals_avg', 1.0)
    a_avg = stats.get('away_goals_avg', 1.0)
    
    # Generar 10,000 escenarios para máxima precisión
    s_home = np.random.poisson(h_avg, 10000)
    s_away = np.random.poisson(a_avg, 10000)
    total_g = s_home + s_away
    
    # Mapeo exacto a las llaves que espera el Cerebro
    return {
        "Resultado Final (Local)": np.mean(s_home > s_away),
        "Resultado Final (Empate)": np.mean(s_home == s_away),
        "Resultado Final (Visitante)": np.mean(s_away > s_home),
        "Doble Oportunidad": np.mean(s_home >= s_away),
        "Ambos Equipos Anotan": np.mean((s_home > 0) & (s_away > 0)),
        "Total Goles Over 1.5": np.mean(total_g > 1.5),
        "Total Goles Over 2.5": np.mean(total_g > 2.5),
        "Total Goles Over 3.5": np.mean(total_g > 3.5),
        "Total Goles Under 2.5": np.mean(total_g < 2.5),
        "1ra Mitad Total Over 0.5": np.mean(np.random.poisson((h_avg+a_avg)*0.45, 10000) > 0.5),
        "Resultado / Ambos Anotan": np.mean((s_home > s_away) & (s_away > 0)),
        "Resultado / Over 2.5": np.mean((s_home > s_away) & (total_g > 2.5)),
        "Doble Oportunidad / Over 1.5": np.mean((s_home >= s_away) & (total_g > 1.5))
    }

