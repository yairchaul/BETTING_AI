import numpy as np
import streamlit as st
import requests

SIMULATIONS = 20000

def adjusted_lambda(home_stats, away_stats):
    league_avg = 1.35
    home_attack = home_stats.get("attack", 50)
    home_def = home_stats.get("defense", 50)
    away_attack = away_stats.get("attack", 50)
    away_def = away_stats.get("defense", 50)
    home_lambda = league_avg * (home_attack / 50) * (50 / away_def)
    away_lambda = league_avg * (away_attack / 50) * (50 / home_def)
    home_lambda *= 1.12
    return home_lambda, away_lambda

def run_simulations(stats):
    try:
        lam_home, lam_away = adjusted_lambda(stats.get("home", {}), stats.get("away", {}))
        noise_home = np.random.normal(1, 0.12, SIMULATIONS)
        noise_away = np.random.normal(1, 0.12, SIMULATIONS)
        goals_home = np.random.poisson(lam_home * noise_home)
        goals_away = np.random.poisson(lam_away * noise_away)
        total_goals = goals_home + goals_away
        h1_goals = np.random.poisson(lam_home/2 * noise_home) + np.random.poisson(lam_away/2 * noise_away)

        return {
            "Resultado Final (Local)": np.mean(goals_home > goals_away),
            "Resultado Final (Empate)": np.mean(goals_home == goals_away),
            "Resultado Final (Visitante)": np.mean(goals_home < goals_away),
            "Ambos Equipos Anotan": np.mean((goals_home > 0) & (goals_away > 0)),
            "Total Goles Over 2.5": np.mean(total_goals > 2.5),
            "1ra Mitad Total Over 1.5": np.mean(h1_goals > 1.5),
        }
    except Exception as e:
        st.error(f"Simulación falló: {str(e)}")
        return {}

def obtener_mejor_apuesta(partido):
    home = partido.get("home", "Local")
    away = partido.get("away", "Visitante")
    stats = {"home": {"attack": 50, "defense": 50}, "away": {"attack": 50, "defense": 50}}  # fallback por ahora

    probs = run_simulations(stats)
    if not probs:
        return None

    # Fallback simple a odds de imagen
    all_odds = partido.get("all_odds", [])
    odds = {}
    if len(all_odds) >= 3:
        try:
            odds["Resultado Final (Local)"] = float(all_odds[0])
            odds["Resultado Final (Empate)"] = float(all_odds[1])
            odds["Resultado Final (Visitante)"] = float(all_odds[2])
        except:
            pass

    mejores = []
    for mercado, prob in probs.items():
        odd = odds.get(mercado, 0)
        if odd == 0:
            continue
        try:
            odd = float(odd)
            decimal = (odd / 100 + 1) if odd > 0 else (100 / abs(odd) + 1) if odd < 0 else 0
            ev = (prob * decimal) - 1
            if ev > 0.05:
                mejores.append({"mercado": mercado, "prob": prob, "odd": odd, "ev": ev})
        except:
            continue

    if not mejores:
        return None

    mejor = max(mejores, key=lambda x: x["ev"])
    return {
        "match": f"{home} vs {away}",
        "selection": mejor["mercado"],
        "odd": mejor["odd"],
        "probability": mejor["prob"],
        "ev": mejor["ev"]
    }