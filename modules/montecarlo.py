import numpy as np

def run_simulations(stats):
    """
    Simulación con penalización por momios extremos para evitar picks 'locos'.
    """
    h_avg = stats.get('home_goals_avg', 1.2)
    a_avg = stats.get('away_goals_avg', 1.1)
    
    # Simulamos 10k escenarios
    s_home = np.random.poisson(h_avg, 10000)
    s_away = np.random.poisson(a_avg, 10000)
    total_g = s_home + s_away
    
    # Probabilidades base
    prob_local = np.mean(s_home > s_away)
    prob_visitante = np.mean(s_away > s_home)
    
    return {
        "Resultado Final (Local)": prob_local,
        "Resultado Final (Empate)": np.mean(s_home == s_away),
        "Resultado Final (Visitante)": prob_visitante,
        "Total Goles Over 1.5": np.mean(total_g > 1.5),
        "Total Goles Under 2.5": np.mean(total_g < 2.5),
        "Ambos Equipos Anotan": np.mean((s_home > 0) & (s_away > 0))
    }
