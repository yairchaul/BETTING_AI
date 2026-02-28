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
    }
    return probs

def obtener_mejor_apuesta(partido):
    home = partido.get("home", "Local")
    away = partido.get("away", "Visitante")
    stats = get_team_stats(home, away)
    probs = run_simulations(stats)

    # 1. Intentar odds de API
    odds_from_api = fetch_odds(home, away)

    # 2. Decidir qué odds usar (API o fallback imagen)
    if isinstance(odds_from_api, dict) and odds_from_api:
        odds = odds_from_api
    else:
        odds = {}
        all_odds_raw = partido.get("all_odds", [])
        if isinstance(all_odds_raw, list) and len(all_odds_raw) >= 3:
            try:
                cleaned = []
                for o in all_odds_raw[:3]:
                    cleaned_str = str(o).strip().replace(' ', '')
                    if cleaned_str:
                        # Convertir con manejo de + y -
                        if cleaned_str.startswith('+'):
                            cleaned.append(float(cleaned_str))
                        elif cleaned_str.startswith('-'):
                            cleaned.append(float(cleaned_str))
                        else:
                            cleaned.append(float(cleaned_str))
                    else:
                        cleaned.append(0.0)
                if all(c != 0.0 for c in cleaned):
                    odds["Resultado Final (Local)"] = cleaned[0]
                    odds["Resultado Final (Empate)"] = cleaned[1]
                    odds["Resultado Final (Visitante)"] = cleaned[2]
            except Exception as conv_err:
                st.warning(f"Conversión de momios fallida: {all_odds_raw} → {str(conv_err)}")

    # 3. Calcular EV solo si hay odds válidos
    mejores = []
    for mercado, prob in probs.items():
        odd_raw = odds.get(mercado)
        if odd_raw is None or odd_raw == 0:
            continue

        try:
            odd = float(odd_raw)
        except (ValueError, TypeError):
            continue

        decimal = (odd / 100 + 1) if odd > 0 else (100 / abs(odd) + 1) if odd < 0 else 0
        if decimal <= 1:
            continue

        ev = (prob * decimal) - 1
        if ev > 0.05:
            mejores.append({"mercado": mercado, "prob": prob, "odd": odd, "ev": ev})

    if mejores:
        mejor = max(mejores, key=lambda x: x["ev"])
        return {
            "match": f"{home} vs {away}",
            "selection": mejor["mercado"],
            "odd": mejor["odd"],
            "probability": mejor["prob"],
            "ev": mejor["ev"]
        }
    
    return None