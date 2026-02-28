import numpy as np
from .stats_fetch import get_team_stats
from .odds_api import fetch_odds

SIMULATIONS = 20000

def adjusted_lambda(home_stats, away_stats):
    # Tu lógica, con stats reales ahora
    league_avg = 1.35
    home_lambda = league_avg * (home_stats["attack"] / 50) * (50 / away_stats["defense"])
    away_lambda = league_avg * (away_stats["attack"] / 50) * (50 / home_stats["defense"])
    home_lambda *= 1.12
    return home_lambda, away_lambda

def run_simulations(stats):
    lam_home, lam_away = adjusted_lambda(stats["home"], stats["away"])
    noise_home = np.random.normal(1, 0.12, SIMULATIONS)
    noise_away = np.random.normal(1, 0.12, SIMULATIONS)
    goals_home = np.random.poisson(lam_home * noise_home)
    goals_away = np.random.poisson(lam_away * noise_away)
    total_goals = goals_home + goals_away
    h1_goals = np.random.poisson(lam_home/2 * noise_home) + np.random.poisson(lam_away/2 * noise_away)  # Aprox 1ra mitad

    probs = {
        "Resultado Final (Local)": np.mean(goals_home > goals_away),
        "Resultado Final (Empate)": np.mean(goals_home == goals_away),
        "Resultado Final (Visitante)": np.mean(goals_home < goals_away),
        "Ambos Equipos Anotan": np.mean((goals_home > 0) & (goals_away > 0)),
        "Total Goles Over 2.5": np.mean(total_goals > 2.5),  # Añade under, ajusta thresholds
        "1ra Mitad Total Over 1.5": np.mean(h1_goals > 1.5),  # Expande
        # Añade combos: e.g. "Local + Over 2.5": np.mean((goals_home > goals_away) & (total_goals > 2.5))
    }
    return probs

def obtener_mejor_apuesta(partido):
    stats = get_team_stats(partido["home"], partido["away"])
    probs = run_simulations(stats)
    odds = fetch_odds(partido["home"], partido["away"]) or partido["all_odds"]  # Fallback a imagen

    mejores = []
    for mercado, prob in probs.items():
        odd = odds.get(mercado, 0)
        if odd > 0:  # Americano positivo
            decimal = odd / 100 + 1
        elif odd < 0:
            decimal = 100 / abs(odd) + 1
        else:
            continue
        ev = (prob * decimal) - 1
        if ev > 0.05:  # Threshold value
            mejores.append({"mercado": mercado, "prob": prob, "odd": odd, "ev": ev})

    if mejores:
        mejor = max(mejores, key=lambda x: x["ev"])
        return PickResult(match=f"{partido['home']} vs {partido['away']}", selection=mejor["mercado"], odd=mejor["odd"], probability=mejor["prob"], ev=mejor["ev"])
    return None