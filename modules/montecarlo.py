import numpy as np
import numpy as np


SIMULATIONS = 20000


def adjusted_lambda(home_stats, away_stats):

    home_attack = home_stats["attack"]
    home_def = home_stats["defense"]

    away_attack = away_stats["attack"]
    away_def = away_stats["defense"]

    league_avg = 1.35

    # ataque vs defensa rival
    home_lambda = league_avg * (home_attack / 50) * (50 / away_def)
    away_lambda = league_avg * (away_attack / 50) * (50 / home_def)

    # ventaja local REAL
    home_lambda *= 1.12

    return home_lambda, away_lambda


def run_simulations(stats):

    home_stats = stats["home"]
    away_stats = stats["away"]

    lam_home, lam_away = adjusted_lambda(home_stats, away_stats)

    # VARIANZA REALISTA
    noise_home = np.random.normal(1, 0.12, SIMULATIONS)
    noise_away = np.random.normal(1, 0.12, SIMULATIONS)

    goals_home = np.random.poisson(lam_home * noise_home)
    goals_away = np.random.poisson(lam_away * noise_away)

    total_goals = goals_home + goals_away

    home_win = np.mean(goals_home > goals_away)
    draw = np.mean(goals_home == goals_away)
    away_win = np.mean(goals_away > goals_home)

    return {
        "Resultado Final (Local)": home_win,
        "Resultado Final (Empate)": draw,
        "Resultado Final (Visitante)": away_win,

        "Doble Oportunidad Local": home_win + draw,
        "Doble Oportunidad Visitante": away_win + draw,

        "Total Goles Over 1.5": np.mean(total_goals > 1.5),
        "Total Goles Over 2.5": np.mean(total_goals > 2.5),
        "Total Goles Under 2.5": np.mean(total_goals < 2.5),

        "Ambos Anotan": np.mean(
            (goals_home > 0) & (goals_away > 0)
        ),
    }
