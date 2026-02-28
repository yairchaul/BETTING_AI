import requests
import numpy as np
import streamlit as st
import unicodedata

SIMULATIONS = 20000

def limpiar_texto(texto):
    """Elimina tildes y convierte a minúsculas para una búsqueda más fácil."""
    texto = unicodedata.normalize('NFD', texto)
    texto = "".join([c for c in texto if unicodedata.category(c) != 'Mn'])
    return texto.lower().strip()

def validar_y_obtener_stats(nombre_equipo):
    """Busca equipos de forma elástica con 3 niveles de re-intento."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Limpieza inicial
        nombre_query = limpiar_texto(nombre_equipo)
        # Quitar palabras comunes que ensucian la búsqueda
        ruido = ["real", "atletico", "de", "fc", "club", "borussia", "union"]
        palabras = [p for p in nombre_query.split() if p not in ruido]
        
        # NIVEL 1: Búsqueda exacta
        url = f"https://v3.football.api-sports.io/teams?search={nombre_query}"
        response = requests.get(url, headers=headers).json()

        # NIVEL 2: Si falla, buscar la palabra más larga y distintiva (ej. 'Cambaceres')
        if response.get('results', 0) == 0 and palabras:
            palabra_clave = max(palabras, key=len)
            url = f"https://v3.football.api-sports.io/teams?search={palabra_clave}"
            response = requests.get(url, headers=headers).json()

        if response.get('results', 0) > 0:
            # Seleccionar el resultado más relevante
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
    """Analiza los últimos 5 partidos para determinar poder de ataque y defensa."""
    try:
        api_key = st.secrets["football_api_key"]
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        headers = {'x-apisports-key': api_key}
        response = requests.get(url, headers=headers).json()
        
        goles_anotados = []
        goles_recibidos = []
        
        for game in response.get('response', []):
            es_local = game['teams']['home']['id'] == team_id
            goles_anotados.append(game['goals']['home'] if es_local else game['goals']['away'])
            goles_recibidos.append(game['goals']['away'] if es_local else game['goals']['home'])
            
        ataque = min(100, (sum(goles_anotados or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(goles_recibidos or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    """Simulación Poisson para encontrar el mercado más seguro."""
    lam_h = 1.35 * (stats_h["attack"]/50) * (50/stats_a["defense"])
    lam_a = 1.10 * (stats_a["attack"]/50) * (50/stats_h["defense"])
    
    h_g = np.random.poisson(lam_h, SIMULATIONS)
    a_g = np.random.poisson(lam_a, SIMULATIONS)
    
    p_1 = np.mean(h_g > a_g)
    p_2 = np.mean(a_g > h_g)
    p_1x = np.mean(h_g >= a_g)
    
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
