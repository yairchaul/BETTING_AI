import numpy as np

def run_simulation(home_attack=1.3, home_defense=1.1, away_attack=1.2, away_defense=1.2, simulations=10000):
    """Simulación Monte Carlo de partido"""
    
    league_avg = 1.35
    
    # Goles esperados
    lambda_home = league_avg * (home_attack / 1.2) * (1.2 / away_defense) * 1.1
    lambda_away = league_avg * (away_attack / 1.2) * (1.2 / home_defense)
    
    # Ruido
    noise_home = np.random.normal(1, 0.1, simulations)
    noise_away = np.random.normal(1, 0.1, simulations)
    
    # Simular goles
    goals_home = np.random.poisson(lambda_home * noise_home)
    goals_away = np.random.poisson(lambda_away * noise_away)
    total_goals = goals_home + goals_away
    
    return {
        'local_gana': float(np.mean(goals_home > goals_away)),
        'empate': float(np.mean(goals_home == goals_away)),
        'visitante_gana': float(np.mean(goals_away > goals_home)),
        'over_1.5': float(np.mean(total_goals > 1.5)),
        'over_2.5': float(np.mean(total_goals > 2.5)),
        'under_2.5': float(np.mean(total_goals < 2.5)),
        'btts': float(np.mean((goals_home > 0) & (goals_away > 0)))
    }
