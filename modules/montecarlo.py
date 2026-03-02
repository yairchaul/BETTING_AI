import numpy as np

def run_simulation(home_attack=1.3, home_defense=1.1, away_attack=1.2, away_defense=1.2, simulations=20000):
    """Simulación Monte Carlo con análisis detallado de todos los mercados"""
    
    league_avg = 1.35
    
    # Goles esperados
    lambda_home = league_avg * (home_attack / 1.2) * (1.2 / away_defense) * 1.1
    lambda_away = league_avg * (away_attack / 1.2) * (1.2 / home_defense)
    
    # Generar goles minuto a minuto (simplificado)
    noise_home = np.random.normal(1, 0.1, simulations)
    noise_away = np.random.normal(1, 0.1, simulations)
    
    goals_home = np.random.poisson(lambda_home * noise_home)
    goals_away = np.random.poisson(lambda_away * noise_away)
    total_goals = goals_home + goals_away
    
    # Simular goles en primer tiempo (asumiendo 45% de los goles en 1T)
    first_half_goals = np.random.binomial(total_goals.astype(int), 0.45)
    second_half_goals = total_goals - first_half_goals
    
    # Análisis para equipos goleadores (como PSV)
    high_scoring_threshold = 5.5
    prob_over_5_5 = np.mean(total_goals > high_scoring_threshold)
    
    # Probabilidad de que el equipo local sea goleador
    local_high_scorer = np.mean(goals_home >= 3)  # 3+ goles del local
    away_high_scorer = np.mean(goals_away >= 3)   # 3+ goles del visitante
    
    # Ambos equipos anotan en primer tiempo
    btts_first_half = np.mean((first_half_goals > 0) & 
                               ((goals_home > 0) & (goals_away > 0)) & 
                               (first_half_goals <= goals_home + goals_away))
    
    # Over 1.5 en primer tiempo
    over_1_5_first_half = np.mean(first_half_goals > 1.5)
    
    # Over 0.5 en primer tiempo
    over_0_5_first_half = np.mean(first_half_goals > 0.5)
    
    # Métricas de goleada
    home_win_by_2plus = np.mean((goals_home - goals_away) >= 2)
    away_win_by_2plus = np.mean((goals_away - goals_home) >= 2)
    
    return {
        # Mercados básicos
        'local_gana': float(np.mean(goals_home > goals_away)),
        'empate': float(np.mean(goals_home == goals_away)),
        'visitante_gana': float(np.mean(goals_away > goals_home)),
        
        # Totales de goles
        'over_0.5': float(np.mean(total_goals > 0.5)),
        'over_1.5': float(np.mean(total_goals > 1.5)),
        'over_2.5': float(np.mean(total_goals > 2.5)),
        'over_3.5': float(np.mean(total_goals > 3.5)),
        'over_4.5': float(np.mean(total_goals > 4.5)),
        'over_5.5': float(prob_over_5_5),  # ¡Para equipos como PSV!
        
        # Primer tiempo
        'over_0.5_1t': float(over_0_5_first_half),
        'over_1.5_1t': float(over_1_5_first_half),
        'btts_1t': float(btts_first_half),
        
        # Ambos anotan
        'btts': float(np.mean((goals_home > 0) & (goals_away > 0))),
        
        # Handicaps y goleadas
        'local_gana_handicap_-1.5': float(np.mean((goals_home - goals_away) >= 2)),
        'visitante_gana_handicap_-1.5': float(np.mean((goals_away - goals_home) >= 2)),
        'local_gana_por_2+': float(home_win_by_2plus),
        'visitante_gana_por_2+': float(away_win_by_2plus),
        
        # Equipos goleadores
        'local_marca_3+': float(local_high_scorer),
        'visitante_marca_3+': float(away_high_scorer),
        
        # Goles totales esperados
        'goles_promedio': float(np.mean(total_goals))
    }
