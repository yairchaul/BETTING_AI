import numpy as np

def run_simulations(stats):
    h_avg = stats.get('home_goals_avg', 1.3)
    a_avg = stats.get('away_goals_avg', 1.1)
    
    # Simulamos 10,000 partidos
    s_home = np.random.poisson(h_avg, 10000)
    s_away = np.random.poisson(a_avg, 10000)
    
    return {
        "Resultado Final (Local)": np.mean(s_home > s_away),
        "Resultado Final (Empate)": np.mean(s_home == s_away),
        "Resultado Final (Visitante)": np.mean(s_away > s_home),
        "Total Goles Over 1.5": np.mean((s_home + s_away) > 1.5),
        "Total Goles Under 2.5": np.mean((s_home + s_away) < 2.5)
    }
