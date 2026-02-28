import requests
import numpy as np
import streamlit as st

SIMULATIONS = 20000

def validar_y_obtener_stats(nombre_equipo):
    """Busca el equipo en la API con re-intento elástico si falla el nombre largo."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Intento 1: Nombre completo (limpiando términos comunes)
        nombre_limpio = nombre_equipo.replace("Borussia", "").replace("Union", "").strip()
        # Si el nombre es muy largo, probamos con la palabra clave principal
        palabras = nombre_equipo.split()
        busqueda_principal = palabras[0] if len(palabras[0]) > 3 else nombre_equipo

        url = f"https://v3.football.api-sports.io/teams?search={nombre_equipo.strip()}"
        response = requests.get(url, headers=headers).json()

        # Intento 2: Si falla, buscamos solo la palabra clave
        if response.get('results', 0) == 0:
            url = f"https://v3.football.api-sports.io/teams?search={busqueda_principal}"
            response = requests.get(url, headers=headers).json()

        if response.get('results', 0) > 0:
            # Seleccionamos el primer resultado que sea un club real
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
    """Extrae los goles de los últimos 5 partidos para calcular ataque/defensa real."""
    try:
        api_key = st.secrets["football_api_key"]
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        headers = {'x-apisports-key': api_key}
        response = requests.get(url, headers=headers).json()
        
        g_h, g_r = [], []
        for game in response.get('response', []):
            is_home = game['teams']['home']['id'] == team_id
            # Sumamos goles anotados y recibidos
            g_h.append(game['goals']['home'] if is_home else game['goals']['away'])
            g_r.append(game['goals']['away'] if is_home else game['goals']['home'])
            
        ataque = min(100, (sum(g_h or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(g_r or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    """Simulación Poisson para elegir el pick basado en datos reales."""
    lam_h = 1.35 * (stats_h["attack"]/50) * (50/stats_a["defense"])
    lam_a = 1.10 * (stats_a["attack"]/50) * (50/stats_h["defense"])
    
    h_g = np.random.poisson(lam_h, SIMULATIONS)
    a_g = np.random.poisson(lam_a, SIMULATIONS)
    
    prob_1 = np.mean(h_g > a_g)
    prob_2 = np.mean(a_g > h_g)
    
    if prob_1 > 0.52:
        res = {"label": f"Gana {partido['home']}", "prob": prob_1, "odd": partido['odds'][0]}
    elif prob_2 > 0.52:
        res = {"label": f"Gana {partido['away']}", "prob": prob_2, "odd": partido['odds'][2]}
    else:
        res = {"label": "Local o Empate", "prob": np.mean(h_g >= a_g), "odd": "-210"}
        
    return {
        "match": f"{partido['home']} vs {partido['away']}",
        "selection": res["label"],
        "odd": res["odd"],
        "probability": res["prob"]
    }
