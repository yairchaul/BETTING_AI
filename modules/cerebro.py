import requests
import numpy as np
import streamlit as st
import unicodedata

SIMULATIONS = 20000

def normalizar_nombre(texto):
    """Elimina tildes y ruidos para facilitar la búsqueda."""
    texto = unicodedata.normalize('NFD', texto)
    texto = "".join([c for c in texto if unicodedata.category(c) != 'Mn'])
    return texto.lower().strip()

def validar_y_obtener_stats(nombre_equipo):
    """Búsqueda inteligente: Intento exacto -> Alias -> Palabra clave."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        nombre_limpio = normalizar_nombre(nombre_equipo)
        
        # Mapeo de alias para nombres ultra-comunes o abreviados
        alias_map = {
            "psg": "Paris Saint Germain",
            "le havre": "Le Havre",
            "monchengladbach": "Mgladbach",
            "atletico madrid": "Atletico de Madrid",
            "cambaceres": "Defensores de Cambaceres",
            "argentino de rosario": "Argentino Rosario",
            "bari youth": "Bari U19",
            "crotone youth": "Crotone U19",
            "pisa youth": "Pisa U19"
        }
        
        for clave, valor in alias_map.items():
            if clave in nombre_limpio:
                nombre_limpio = valor
                break

        # PASO 1: Búsqueda directa
        url = f"https://v3.football.api-sports.io/teams?search={nombre_limpio}"
        response = requests.get(url, headers=headers).json()

        # PASO 2: Si falla, buscar solo la palabra más larga (ej. de 'Real Oviedo' buscar 'Oviedo')
        if response.get('results', 0) == 0:
            palabras = [p for p in nombre_limpio.split() if len(p) > 3]
            if palabras:
                principal = max(palabras, key=len)
                url = f"https://v3.football.api-sports.io/teams?search={principal}"
                response = requests.get(url, headers=headers).json()

        if response.get('results', 0) > 0:
            # Seleccionamos el primer equipo (el más relevante)
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
    """Extrae el rendimiento real (goles) de los últimos 5 partidos."""
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
            
        # Calculamos poder de ataque y defensa (0-100)
        ataque = min(100, (sum(g_hechos or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(g_recibidos or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    """Simulación Poisson para encontrar la probabilidad de 1X."""
    lam_h = 1.35 * (stats_h["attack"]/50) * (50/stats_a["defense"])
    lam_a = 1.10 * (stats_a["attack"]/50) * (50/stats_h["defense"])
    
    h_g = np.random.poisson(lam_h, SIMULATIONS)
    a_g = np.random.poisson(lam_a, SIMULATIONS)
    
    prob_1x = np.mean(h_g >= a_g)
    
    return {
        "selection": "Local o Empate (1X)",
        "odd": "-115",
        "probability": prob_1x
    }
