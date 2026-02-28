import requests
import numpy as np
import streamlit as st
import unicodedata

SIMULATIONS = 20000

def buscar_equipos_v2(nombre_query):
    """Motor de búsqueda elástico que emula la flexibilidad de Google."""
    try:
        if len(nombre_query) < 3: return []
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Normalización para ignorar acentos y mayúsculas
        query = unicodedata.normalize('NFD', nombre_query)
        query = "".join([c for c in query if unicodedata.category(c) != 'Mn']).lower()
        
        # Intentar búsqueda general
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

def extraer_stats_avanzadas(team_id):
    """Extrae métricas de rendimiento (ataque/defensa) basadas en los últimos juegos."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        # Obtenemos los últimos 10 partidos para mayor precisión estadística
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
        response = requests.get(url, headers=headers).json()
        
        goles_favor = []
        goles_contra = []
        
        for game in response.get('response', []):
            is_home = game['teams']['home']['id'] == team_id
            goles_favor.append(game['goals']['home'] if is_home else game['goals']['away'])
            goles_contra.append(game['goals']['away'] if is_home else game['goals']['home'])
            
        # Cálculo de potencia relativa (Similar a los algoritmos de predicción de Google)
        avg_favor = sum(goles_favor) / len(goles_favor) if goles_favor else 1.0
        avg_contra = sum(goles_contra) / len(goles_contra) if goles_contra else 1.2
        
        return {"attack_power": avg_favor, "defense_weakness": avg_contra}
    except:
        return {"attack_power": 1.1, "defense_weakness": 1.1}

def simular_probabilidades(stats_h, stats_a):
    """Simulación de Monte Carlo con Distribución de Poisson."""
    # Factor de ventaja de localía (10% extra para el local)
    home_exp = stats_h["attack_power"] * stats_a["defense_weakness"] * 1.1
    away_exp = stats_a["attack_power"] * stats_h["defense_weakness"]
    
    # Generamos 20,000 resultados posibles del partido
    home_goals = np.random.poisson(home_exp, SIMULATIONS)
    away_goals = np.random.poisson(away_exp, SIMULATIONS)
    
    # Calculamos probabilidades
    prob_h = np.mean(home_goals > away_goals)
    prob_draw = np.mean(home_goals == away_goals)
    prob_a = np.mean(away_goals > home_goals)
    
    # Probabilidad de Doble Oportunidad (1X)
    prob_1x = prob_h + prob_draw
    
    return {
        "local": prob_h,
        "empate": prob_draw,
        "visitante": prob_a,
        "doble_oportunidad": prob_1x
    }
