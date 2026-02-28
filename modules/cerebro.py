import requests
import numpy as np
import streamlit as st
import unicodedata

SIMULATIONS = 20000

def buscar_posibles_equipos(nombre_query):
    """Busca en la API y devuelve una lista de candidatos (nombre e ID)."""
    try:
        if len(nombre_query) < 3: return []
        
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Limpieza básica para la búsqueda
        query = unicodedata.normalize('NFD', nombre_query)
        query = "".join([c for c in query if unicodedata.category(c) != 'Mn']).lower()
        
        url = f"https://v3.football.api-sports.io/teams?search={query}"
        response = requests.get(url, headers=headers).json()
        
        candidatos = []
        if response.get('results', 0) > 0:
            for item in response['response']:
                candidatos.append({
                    "display": f"{item['team']['name']} ({item['team']['country']})",
                    "id": item['team']['id'],
                    "logo": item['team']['logo'],
                    "name": item['team']['name']
                })
        return candidatos
    except Exception:
        return []

def obtener_forma_reciente(team_id):
    """Extrae potencia de ataque y defensa real de los últimos 5 partidos."""
    try:
        api_key = st.secrets["football_api_key"]
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        headers = {'x-apisports-key': api_key}
        response = requests.get(url, headers=headers).json()
        
        g_hechos, g_recibidos = [], []
        for game in response.get('response', []):
            es_local = game['teams']['home']['id'] == team_id
            g_hechos.append(game['goals']['home'] if es_local else game['goals']['away'])
            g_recibidos.append(game['goals']['away'] if es_local else game['goals']['home'])
            
        ataque = min(100, (sum(g_hechos or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(g_recibidos or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(stats_h, stats_a):
    """Simulación Poisson para encontrar probabilidad real."""
    lam_h = 1.35 * (stats_h["attack"]/50) * (50/stats_a["defense"])
    lam_a = 1.10 * (stats_a["attack"]/50) * (50/stats_h["defense"])
    
    h_g = np.random.poisson(lam_h, SIMULATIONS)
    a_g = np.random.poisson(lam_a, SIMULATIONS)
    
    prob_1x = np.mean(h_g >= a_g)
    
    return {
        "selection": "Local o Empate (1X)",
        "probability": prob_1x
    }
