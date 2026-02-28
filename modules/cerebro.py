import requests
import numpy as np
import streamlit as st

SIMULATIONS = 20000

def validar_y_obtener_stats(nombre_equipo):
    """Busca el equipo en la API para confirmar existencia y obtener ID."""
    try:
        api_key = st.secrets["football_api_key"]
        # Limpieza agresiva para mejorar la búsqueda
        nombre_limpio = nombre_equipo.replace("FC", "").replace("Youth", "").replace("U19", "").replace("U23", "").strip()
        
        url = f"https://v3.football.api-sports.io/teams?search={nombre_limpio}"
        headers = {'x-apisports-key': api_key}
        
        response = requests.get(url, headers=headers).json()
        if response.get('results', 0) > 0:
            team_data = response['response'][0]['team']
            return {
                "nombre_real": team_data['name'],
                "logo": team_data['logo'],
                "id": team_data['id'],
                "valido": True
            }
        return {"valido": False}
    except:
        return {"valido": False}

def obtener_forma_reciente(team_id):
    """Extrae goles de los últimos 5 partidos desde la API."""
    try:
        api_key = st.secrets["football_api_key"]
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        headers = {'x-apisports-key': api_key}
        response = requests.get(url, headers=headers).json()
        
        g_h, g_r = [], []
        for game in response.get('response', []):
            is_home = game['teams']['home']['id'] == team_id
            g_h.append(game['goals']['home'] if is_home else game['goals']['away'])
            g_r.append(game['goals']['away'] if is_home else game['goals']['home'])
            
        # Normalización de fuerza 0-100
        ataque = min(100, (sum(g_h or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(g_r or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    """Simulación Poisson para determinar el pick más seguro."""
    lam_h = 1.35 * (stats_h["attack"]/50) * (50/stats_a["defense"])
    lam_a = 1.10 * (stats_a["attack"]/50) * (50/stats_h["defense"])
    
    h_g = np.random.poisson(lam_h, SIMULATIONS)
    a_g = np.random.poisson(lam_a, SIMULATIONS)
    
    prob_1 = np.mean(h_g > a_g)
    prob_2 = np.mean(a_g > h_g)
    prob_bts = np.mean((h_g > 0) & (a_g > 0))
    
    # Lógica de mercado: Seleccionamos lo más probable
    if prob_1 > 0.50:
        res = {"label": f"Gana {partido['home']}", "prob": prob_1, "odd": partido['odds'][0]}
    elif prob_2 > 0.50:
        res = {"label": f"Gana {partido['away']}", "prob": prob_2, "odd": partido['odds'][2]}
    elif prob_bts > 0.60:
        res = {"label": "Ambos Anotan", "prob": prob_bts, "odd": "-110"}
    else:
        res = {"label": "Local o Empate", "prob": np.mean(h_g >= a_g), "odd": "-200"}
        
    return {
        "match": f"{partido['home']} vs {partido['away']}",
        "selection": res["label"],
        "odd": res["odd"],
        "probability": res["prob"]
    }
