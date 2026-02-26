import numpy as np

SIMULATIONS = 20000

def adjusted_lambda(home_stats, away_stats):
    # Mantenemos tu lógica de ataque/defensa funcional
    home_attack = home_stats.get("attack", 50)
    home_def = home_stats.get("defense", 50)
    away_attack = away_stats.get("attack", 50)
    away_def = away_stats.get("defense", 50)

    league_avg = 1.35
    home_lambda = league_avg * (home_attack / 50) * (50 / away_def)
    away_lambda = league_avg * (away_attack / 50) * (50 / home_def)
    home_lambda *= 1.12  # Ventaja local

    return home_lambda, away_lambda

def run_simulations(stats):
    # Extraemos stats de forma segura para evitar errores de llave
    home_data = stats.get("home", stats) 
    away_data = stats.get("away", stats)

    lam_home, lam_away = adjusted_lambda(home_data, away_data)

    # Mantenemos tu VARIANZA REALISTA
    noise_home = np.random.normal(1, 0.12, SIMULATIONS)
    noise_away = np.random.normal(1, 0.12, SIMULATIONS)

    goals_home = np.random.poisson(lam_home * noise_home)
    goals_away = np.random.poisson(lam_away * noise_away)
    total_goals = goals_home + goals_away

    # Probabilidades base
    home_win = np.mean(goals_home > goals_away)
    draw = np.mean(goals_home == goals_away)
    away_win = np.mean(goals_away > goals_home)

    # NUEVA: Doble Oportunidad (Local o Empate) + Over 1.5
    # Esta es la que pediste para el parlay
    prob_do_over = np.mean(((goals_home >= goals_away)) & (total_goals > 1.5))

    return {
        "Resultado Final (Local)": home_win,
        "Resultado Final (Empate)": draw,
        "Resultado Final (Visitante)": away_win,
        "Doble Oportunidad / Over 1.5": prob_do_over,
        "Total Goles Over 1.5": np.mean(total_goals > 1.5),
        "Total Goles Under 2.5": np.mean(total_goals < 2.5),
        "Ambos Anotan": np.mean((goals_home > 0) & (goals_away > 0))
    }

