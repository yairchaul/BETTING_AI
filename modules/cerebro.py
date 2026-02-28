import requests
import numpy as np
import streamlit as st
import unicodedata

SIMULATIONS = 20000

def corregir_nombre_equipo(nombre):
    """Limpia el nombre para que la API de fútbol lo entienda mejor."""
    # Eliminar acentos y pasar a minúsculas
    nombre = "".join(c for c in unicodedata.normalize('NFD', nombre) if unicodedata.category(c) != 'Mn')
    nombre = nombre.lower()
    
    # Mapeo de correcciones comunes (puedes añadir más)
    correcciones = {
        "psg": "Paris Saint Germain",
        "ac le havre": "Le Havre",
        "atletico madrid": "Atletico de Madrid",
        "monchengladbach": "Mgladbach",
        "cambaceres": "Defensores de Cambaceres",
        "argentino de rosario": "Argentino Rosario"
    }
    
    for clave, valor in correcciones.items():
        if clave in nombre:
            return valor
    return nombre

def validar_y_obtener_stats(nombre_equipo):
    """Busca el equipo en la API con re-intentos inteligentes."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # 1. Intentar con nombre corregido
        nombre_query = corregir_nombre_equipo(nombre_equipo)
        
        url = f"https://v3.football.api-sports.io/teams?search={nombre_query}"
        response = requests.get(url, headers=headers).json()

        # 2. Si falla, intentar solo con la palabra más larga (ej. de 'AC Le Havre' buscar 'Havre')
        if response.get('results', 0) == 0:
            palabras = [p for p in nombre_query.split() if len(p) > 3]
            if palabras:
                palabra_clave = max(palabras, key=len)
                url = f"https://v3.football.api-sports.io/teams?search={palabra_clave}"
                response = requests.get(url, headers=headers).json()

        if response.get('results', 0) > 0:
            # Filtramos para obtener el equipo más relevante (usualmente el primero)
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
    """Extrae goles reales de la API."""
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
            
        ataque = min(100, (sum(g_h or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(g_r or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    """Simulación Poisson."""
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
        
    return {**res, "probability": res["prob"]}
