import numpy as np
import requests
import streamlit as st
from .odds_api import fetch_odds  # si ya tienes este archivo, úsalo; si no, lo creamos después

SIMULATIONS = 20000

def get_real_stats(home, away):
    api_key = st.secrets.get("API_FOOTBALL_KEY")
    if not api_key:
        st.warning("No hay API_FOOTBALL_KEY en secrets")
        return {"home": {"attack": 50, "defense": 50}, "away": {"attack": 50, "defense": 50}}

    url = "https://v3.football.api-sports.io/teams/statistics"
    headers = {"x-apisports-key": api_key}

    # Esto es simplificado. En producción busca IDs de equipos primero
    # Por ahora asumimos que tienes league=140 (LaLiga) y season actual
    params_home = {"league": 140, "season": 2025, "team": 541}  # ejemplo IDs, cámbialos por reales
    params_away = {"league": 140, "season": 2025, "team": 529}   # ejemplo

    stats = {"home": {}, "away": {}}

    try:
        r_home = requests.get(url, headers=headers, params=params_home)
        data_home = r_home.json().get("response", {})
        stats["home"]["attack"] = data_home.get("goals", {}).get("for", {}).get("average", {}).get("total", 1.0) * 25
        stats["home"]["defense"] = 100 - (data_home.get("goals", {}).get("against", {}).get("average", {}).get("total", 1.0) * 25)

        r_away = requests.get(url, headers=headers, params=params_away)
        data_away = r_away.json().get("response", {})
        stats["away"]["attack"] = data_away.get("goals", {}).get("for", {}).get("average", {}).get("total", 1.0) * 25
        stats["away"]["defense"] = 100 - (data_away.get("goals", {}).get("against", {}).get("average", {}).get("total", 1.0) * 25)
    except:
        st.warning("Fallo al obtener stats reales, usando defaults")
        stats = {"home": {"attack": 50, "defense": 50}, "away": {"attack": 50, "defense": 50}}

    return stats

def run_simulations(stats):
    lam_home, lam_away = adjusted_lambda(stats["home"], stats["away"])
    noise_h = np.random.normal(1, 0.12, SIMULATIONS)
    noise_a = np.random.normal(1, 0.12, SIMULATIONS)
    g_h = np.random.poisson(lam_home * noise_h)
    g_a = np.random.poisson(lam_away * noise_a)
    total = g_h + g_a
    h1 = np.random.poisson(lam_home/2 * noise_h) + np.random.poisson(lam_away/2 * noise_a)

    return {
        "Resultado Final (Local)": np.mean(g_h > g_a),
        "Resultado Final (Empate)": np.mean(g_h == g_a),
        "Resultado Final (Visitante)": np.mean(g_h < g_a),
        "Ambos Equipos Anotan": np.mean((g_h > 0) & (g_a > 0)),
        "Total Goles Over 2.5": np.mean(total > 2.5),
        "1ra Mitad Total Over 1.5": np.mean(h1 > 1.5),
    }

def obtener_mejor_apuesta(partido):
    home = partido.get("home", "Local")
    away = partido.get("away", "Visitante")
    stats = get_real_stats(home, away)
    probs = run_simulations(stats)

    odds = fetch_odds(home, away) or partido.get("all_odds", [])

    # Si odds es lista de imagen, convertir a dict básico
    if isinstance(odds, list) and len(odds) >= 3:
        try:
            odds = {
                "Resultado Final (Local)": float(odds[0]),
                "Resultado Final (Empate)": float(odds[1]),
                "Resultado Final (Visitante)": float(odds[2])
            }
        except:
            odds = {}

    mejores = []
    for mercado, prob in probs.items():
        odd = odds.get(mercado, 0)
        if not odd:
            continue
        decimal = (odd / 100 + 1) if odd > 0 else (100 / abs(odd) + 1) if odd < 0 else 1
        ev = (prob * decimal) - 1
        if ev > 0.05:
            mejores.append({"mercado": mercado, "prob": prob, "odd": odd, "ev": ev})

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