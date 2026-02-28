import requests
import numpy as np
import streamlit as st

SIMULATIONS = 20000

def validar_y_obtener_stats(nombre_equipo):
    """Busca el equipo en la API para confirmar su existencia."""
    api_key = st.secrets["football_api_key"]
    url = f"https://v3.football.api-sports.io/teams?search={nombre_equipo}"
    headers = {'x-apisports-key': api_key}
    
    try:
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
    """Extrae goles de los últimos 5 partidos para calcular fuerza real."""
    api_key = st.secrets["football_api_key"]
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
    headers = {'x-apisports-key': api_key}
    
    try:
        response = requests.get(url, headers=headers).json()
        goles_hechos = []
        goles_recibidos = []
        
        for game in response.get('response', []):
            is_home = game['teams']['home']['id'] == team_id
            goles_hechos.append(game['goals']['home'] if is_home else game['goals']['away'])
            goles_recibidos.append(game['goals']['away'] if is_home else game['goals']['home'])
            
        # Calcular poder de ataque y defensa (0-100)
        # 1.5 goles/partido promedio se traduce en 70 pts de ataque
        ataque = min(100, (sum(goles_hechos or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(goles_recibidos or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def run_simulations(home_stats, away_stats):
    """Simulación Poisson con datos reales."""
    lam_h = 1.40 * (home_stats["attack"]/50) * (50/away_stats["defense"])
    lam_a = 1.10 * (away_stats["attack"]/50) * (50/home_stats["defense"])
    
    h_goals = np.random.poisson(lam_h, SIMULATIONS)
    a_goals = np.random.poisson(lam_a, SIMULATIONS)
    
    return {
        "1": np.mean(h_goals > a_goals),
        "X": np.mean(h_goals == a_goals),
        "2": np.mean(h_goals < a_goals),
        "Ambos Anotan": np.mean((h_goals > 0) & (a_goals > 0)),
        "Over 2.5": np.mean((h_goals + a_goals) > 2.5)
    }

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    home_name = partido["home"]
    raw_odds = partido["odds"]
    
    probs = run_simulations(stats_h, stats_a)
    opciones = []
    
    # Evaluar 1X2 con momios de la imagen
    mapa = {"1": 0, "X": 1, "2": 2}
    labels = {"1": f"Gana {home_name}", "X": "Empate", "2": "Gana Visitante"}
    
    for clave, idx in mapa.items():
        try:
            momio = int(raw_odds[idx].replace('+', ''))
            dec = (momio/100+1) if momio > 0 else (100/abs(momio)+1)
            prob = probs[clave]
            if prob > 0.48: # Solo si es probable
                opciones.append({"label": labels[clave], "prob": prob, "odd": momio})
        except: continue
        
    if probs["Ambos Anotan"] > 0.63:
        opciones.append({"label": "Ambos Anotan", "prob": probs["Ambos Anotan"], "odd": -110})

    if not opciones: return None
    mejor = max(opciones, key=lambda x: x["prob"])
    return {
        "match": f"{partido['home']} vs {partido['away']}",
        "selection": mejor["label"],
        "odd": mejor["odd"],
        "probability": mejor["prob"],
        "ev": (mejor["prob"] * 1.9) - 1 # Simplificado
    }
