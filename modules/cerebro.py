import requests
import numpy as np
import streamlit as st
import unicodedata

SIMULATIONS = 20000

def normalizar_nombre(texto):
    """Limpia el texto eliminando ruidos y acentos."""
    texto = unicodedata.normalize('NFD', texto)
    texto = "".join([c for c in texto if unicodedata.category(c) != 'Mn'])
    return texto.lower().strip()

def validar_y_obtener_stats(nombre_equipo):
    """Busca el equipo con lógica de corrección automática."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        nombre_limpio = normalizar_nombre(nombre_equipo)
        
        # Diccionario de corrección para errores comunes detectados en tus capturas
        correcciones = {
            "psg": "Paris Saint Germain",
            "ac le havre": "Le Havre",
            "cambaceres": "Defensores de Cambaceres",
            "monchengladbach": "Mgladbach",
            "atletico madrid": "Atletico de Madrid",
            "oviedo": "Real Oviedo",
            "bari youth": "Bari U19",
            "crotone youth": "Crotone U19"
        }
        
        # Aplicar corrección si existe en el diccionario
        for clave, valor in correcciones.items():
            if clave in nombre_limpio:
                nombre_limpio = valor
                break

        # NIVEL 1: Búsqueda con el nombre (corregido o limpio)
        url = f"https://v3.football.api-sports.io/teams?search={nombre_limpio}"
        response = requests.get(url, headers=headers).json()

        # NIVEL 2: Si falla, buscar solo por la palabra más larga y distintiva
        if response.get('results', 0) == 0:
            palabras = [p for p in nombre_limpio.split() if len(p) > 3]
            if palabras:
                principal = max(palabras, key=len)
                url = f"https://v3.football.api-sports.io/teams?search={principal}"
                response = requests.get(url, headers=headers).json()

        if response.get('results', 0) > 0:
            # Retornamos el primer resultado que suele ser el más relevante
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
    """Obtiene los goles de los últimos 5 partidos para el cálculo de probabilidades."""
    try:
        api_key = st.secrets["football_api_key"]
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        headers = {'x-apisports-key': api_key}
        response = requests.get(url, headers=headers).json()
        
        g_anotados, g_recibidos = [], []
        for game in response.get('response', []):
            es_local = game['teams']['home']['id'] == team_id
            g_anotados.append(game['goals']['home'] if es_local else game['goals']['away'])
            g_recibidos.append(game['goals']['away'] if es_local else game['goals']['home'])
            
        ataque = min(100, (sum(g_anotados or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(g_recibidos or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    """Simulación para determinar el mejor pick (Gana o Doble Oportunidad)."""
    lam_h = 1.35 * (stats_h["attack"]/50) * (50/stats_a["defense"])
    lam_a = 1.10 * (stats_a["attack"]/50) * (50/stats_h["defense"])
    
    h_g = np.random.poisson(lam_h, SIMULATIONS)
    a_g = np.random.poisson(lam_a, SIMULATIONS)
    
    p_1 = np.mean(h_g > a_g)
    p_2 = np.mean(a_g > h_g)
    p_1x = np.mean(h_g >= a_g)
    
    # Elección del pick basado en umbrales de probabilidad
    if p_1 > 0.52:
        res = {"label": f"Gana {partido['home']}", "prob": p_1, "odd": partido['odds'][0]}
    elif p_2 > 0.52:
        res = {"label": "Gana Visitante", "prob": p_2, "odd": partido['odds'][2]}
    else:
        res = {"label": "Local o Empate (1X)", "prob": p_1x, "odd": "-230"}
        
    return {**res, "probability": res["prob"]}
