import requests
import numpy as np
import streamlit as st
import unicodedata

SIMULATIONS = 20000

def normalizar_y_limpiar(texto):
    """Elimina acentos, ruidos de ligas y términos comunes de apuestas."""
    # Quitar acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = "".join([c for c in texto if unicodedata.category(c) != 'Mn'])
    texto = texto.lower()
    
    # Lista de ruido a eliminar para mejorar la búsqueda
    ruido = ["fc", "sc", "ii", "youth", "u19", "u23", "atletico", "real", "de", "club", "fk", "idman yurdu"]
    palabras = texto.split()
    filtradas = [p for p in palabras if p not in ruido and len(p) > 2]
    
    return " ".join(filtradas) if filtradas else texto

def validar_y_obtener_stats(nombre_equipo):
    """Busca el equipo usando un sistema de 3 niveles de confianza."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Diccionario de Alias (Equipos que siempre dan problemas)
        alias_comunes = {
            "psg": "Paris Saint Germain",
            "philadelphia union": "Philadelphia Union",
            "toronto": "Toronto FC",
            "cambaceres": "Defensores de Cambaceres",
            "monchengladbach": "Mgladbach",
            "le havre": "Le Havre",
            "bari": "Bari",
            "pisa": "Pisa"
        }

        nombre_buscar = normalizar_y_limpiar(nombre_equipo)
        
        # Verificar si está en el mapa de alias
        for clave, valor in alias_comunes.items():
            if clave in nombre_buscar:
                nombre_buscar = valor
                break

        # Intento 1: Búsqueda con el nombre procesado
        url = f"https://v3.football.api-sports.io/teams?search={nombre_buscar}"
        response = requests.get(url, headers=headers).json()

        # Intento 2: Si falla, buscar solo la palabra más larga y distintiva
        if response.get('results', 0) == 0:
            palabras = nombre_buscar.split()
            if palabras:
                principal = max(palabras, key=len)
                url = f"https://v3.football.api-sports.io/teams?search={principal}"
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
    except Exception:
        return {"valido": False}

def obtener_forma_reciente(team_id):
    """Extrae la potencia de ataque y defensa real de los últimos 5 partidos."""
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
            
        # Normalización de fuerza (0-100)
        ataque = min(100, (sum(g_hechos or [0]) / 7.5) * 50 + 20)
        defensa = min(100, 100 - (sum(g_recibidos or [0]) / 5) * 40)
        return {"attack": ataque, "defense": defensa}
    except:
        return {"attack": 50, "defense": 50}

def obtener_mejor_apuesta(partido, stats_h, stats_a):
    """Simulación de Monte Carlo para encontrar el mercado más probable."""
    lam_h = 1.35 * (stats_h["attack"]/50) * (50/stats_a["defense"])
    lam_a = 1.10 * (stats_a["attack"]/50) * (50/stats_h["defense"])
    
    h_g = np.random.poisson(lam_h, SIMULATIONS)
    a_g = np.random.poisson(lam_a, SIMULATIONS)
    
    prob_1x = np.mean(h_g >= a_g)
    
    return {
        "selection": "Local o Empate (1X)",
        "odd": "-120",
        "probability": prob_1x
    }
