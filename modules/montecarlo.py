import numpy as np

def run_simulations(stats):
    """
    Simulación ajustada para mercados individuales (Sencillos).
    Basado en el análisis de tendencia real de los últimos 5 partidos.
    """
    h_avg = stats.get('home_goals_avg', 1.0)
    a_avg = stats.get('away_goals_avg', 1.0)
    
    # 10,000 simulaciones para precisión
    s_home = np.random.poisson(h_avg, 10000)
    s_away = np.random.poisson(a_avg, 10000)
    total_g = s_home + s_away
    
    # Solo mercados que el OCR detecta directamente en la lista de Caliente
    return {
        "Resultado Final (Local)": np.mean(s_home > s_away),
        "Resultado Final (Empate)": np.mean(s_home == s_away),
        "Resultado Final (Visitante)": np.mean(s_away > s_home),
        "Total Goles Over 1.5": np.mean(total_g > 1.5),
        "Total Goles Over 2.5": np.mean(total_g > 2.5),
        "Total Goles Under 2.5": np.mean(total_g < 2.5),
        "Ambos Equipos Anotan": np.mean((s_home > 0) & (s_away > 0))
    }
