import requests
import numpy as np
import streamlit as st

SIMULATIONS = 20000

def validar_y_obtener_stats(nombre_equipo):
    """Busca equipos de forma elástica si el nombre exacto falla."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Limpieza inicial de términos que ensucian la búsqueda
        nombre_limpio = nombre_equipo.replace("Borussia", "").replace("Real", "").replace("Atletico", "").strip()
        palabras = nombre_equipo.split()
        
        # NIVEL 1: Búsqueda exacta como se escribió
        url = f"https://v3.football.api-sports.io/teams?search={nombre_equipo.strip()}"
        response = requests.get(url, headers=headers).json()

        # NIVEL 2: Si falla, buscar la palabra más larga (ej. 'Monchengladbach' o 'Oviedo')
        if response.get('results', 0) == 0 and len(palabras) > 1:
            palabra_clave = max(palabras, key=len)
            url = f"https://v3.football.api-sports.io/teams?search={palabra_clave}"
            response = requests.get(url, headers=headers).json()

        if response.get('results', 0) > 0:
            # Seleccionamos el primer equipo de la lista de resultados
            team_data = response['response'][0]['team']
            return {
                "nombre_real": team_data['name'],
                "logo": team_data['logo'],
                "id": team_data['id'],
                "valido": True
            }
        
        return {"valido": False}
    except Exception:
        return {"valido": False}

def obtener_forma_reciente(team_id):
    """Analiza los goles de los últimos 5 partidos reales para calcular fuerza."""
    try:
        api_key = st.secrets["football_api_key"]
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        headers = {'x-apisports-key': api_key}
        response = requests.get(url, headers=headers).json()
        
        g_hechos = []
        g_recibidos = []
        
        for game in response.get('response', []):
            es_local = game['teams']['home']['id'] == team_id
            g_hechos.append(game['goals']['home'] if es_local else game['goals']['away'])
            g_recibidos.append(game['goals']['away'] if es_local else game['goals']['home'])
            
        # Cálculo de poder basado en promedio de goles
        ataque = min(100, (sum(g_hechos or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(g_recibidos or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    """Simulación Monte Carlo para encontrar el pick con mayor probabilidad."""
    lam_h = 1.35 * (stats_h["attack"]/50) * (50/stats_a["defense"])
    lam_a = 1.10 * (stats_a["attack"]/50) * (50/stats_h["defense"])
    
    h_g = np.random.poisson(lam_h, SIMULATIONS)
    a_g = np.random.poisson(lam_a, SIMULATIONS)
    
    p_1 = np.mean(h_g > a_g)
    p_2 = np.mean(a_g > h_g)
    p_1x = np.mean(h_g >= a_g)
    
    # Decisión del mercado basado en probabilidad real
    if p_1 > 0.52:
        res = {"label": f"Gana {partido['home']}", "prob": p_1, "odd": partido['odds'][0]}
    elif p_2 > 0.52:
        res = {"label": f"Gana Visitante", "prob": p_2, "odd": partido['odds'][2]}
    else:
        res = {"label": "Local o Empate (1X)", "prob": p_1x, "odd": "-230"}
        
    return {
        "match": f"{partido['home']} vs {partido['away']}",
        "selection": res["label"],
        "odd": res["odd"],
        "probability": res["prob"]
    }
