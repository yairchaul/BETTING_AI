import numpy as np
from .stats_fetch import get_team_stats
from .odds_api import fetch_odds

SIMULATIONS = 20000

def adjusted_lambda(home_stats, away_stats):
    league_avg = 1.35
    home_lambda = league_avg * (home_stats.get("attack", 50) / 50) * (50 / away_stats.get("defense", 50))
    away_lambda = league_avg * (away_stats.get("attack", 50) / 50) * (50 / home_stats.get("defense", 50))
    home_lambda *= 1.12
    return home_lambda, away_lambda

def run_simulations(stats):
    lam_home, lam_away = adjusted_lambda(stats.get("home", {}), stats.get("away", {}))
    noise_home = np.random.normal(1, 0.12, SIMULATIONS)
    noise_away = np.random.normal(1, 0.12, SIMULATIONS)
    goals_home = np.random.poisson(lam_home * noise_home)
    goals_away = np.random.poisson(lam_away * noise_away)
    total_goals = goals_home + goals_away
    h1_goals = np.random.poisson(lam_home/2 * noise_home) + np.random.poisson(lam_away/2 * noise_away)

    probs = {
        "Resultado Final (Local)": np.mean(goals_home > goals_away),
        "Resultado Final (Empate)": np.mean(goals_home == goals_away),
        "Resultado Final (Visitante)": np.mean(goals_home < goals_away),
        "Ambos Equipos Anotan": np.mean((goals_home > 0) & (goals_away > 0)),
        "Total Goles Over 2.5": np.mean(total_goals > 2.5),
        "1ra Mitad Total Over 1.5": np.mean(h1_goals > 1.5),
        # Añade más mercados como "Resultado Final + Over 1.5": np.mean((goals_home > goals_away) & (total_goals > 1.5))
    }
    return probs

def obtener_mejor_apuesta(partido):
    stats = get_team_stats(partido.get("home", "Local"), partido.get("away", "Visitante"))
    probs = run_simulations(stats)
    
    odds_from_api = fetch_odds(partido.get("home", "Local"), partido.get("away", "Visitante"))
    
    if odds_from_api and isinstance(odds_from_api, dict):
        odds = odds_from_api
    else:
        all_odds = partido.get("all_odds", [])
        odds = {}
        if len(all_odds) >= 3:
            try:
                odds["Resultado Final (Local)"] = float(all_odds[0])
                odds["Resultado Final (Empate)"] = float(all_odds[1])
                odds["Resultado Final (Visitante)"] = float(all_odds[2])
            except ValueError:
                st.warning(f"Momios no numéricos en fila: {all_odds}")
                odds = {}
        else:
            st.warning(f"Solo {len(all_odds)} momios detectados para {partido.get('home', 'Desconocido')} vs {partido.get('away', 'Desconocido')}")

    mejores = []
    for mercado, prob in probs.items():
        odd = odds.get(mercado, 0)
        if odd == 0:
            continue
        try:
            odd = float(odd)
        except ValueError:
            continue
        decimal = (odd / 100 + 1) if odd > 0 else (100 / abs(odd) + 1)
        ev = (prob * decimal) - 1
        if ev > 0.05:
            mejores.append({"mercado": mercado, "prob": prob, "odd": odd, "ev": ev})

    if mejores:
        mejor = max(mejores, key=lambda x: x["ev"])
        return PickResult(match=f"{partido.get('home', 'Local')} vs {partido.get('away', 'Visitante')}", selection=mejor["mercado"], odd=mejor["odd"], probability=mejor["prob"], ev=mejor["ev"])
    return None