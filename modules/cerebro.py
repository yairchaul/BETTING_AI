# modules/cerebro.py (mejorado para usar stats reales)
import requests
import numpy as np
import streamlit as st
import unicodedata
from modules.montecarlo import run_simulations

SIMULATIONS = 20000

def buscar_equipos_v2(nombre_query):
    """Tu función existente - la dejamos igual"""
    # ... (código existente) ...

def extraer_stats_avanzadas(team_id):
    """Versión mejorada que devuelve stats reales en lugar de fijos"""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Obtener últimos 10 partidos
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
        response = requests.get(url, headers=headers).json()
        
        if not response.get('response'):
            return None
        
        # Calcular estadísticas
        goles_favor = []
        goles_contra = []
        posesion = []
        tiros_meta = []
        
        for game in response['response']:
            is_home = game['teams']['home']['id'] == team_id
            
            # Goles
            goles_favor.append(game['goals']['home'] if is_home else game['goals']['away'])
            goles_contra.append(game['goals']['away'] if is_home else game['goals']['home'])
            
            # Estadísticas adicionales si están disponibles
            if 'statistics' in game:
                stats = game['statistics'][0]['statistics'] if game['statistics'] else []
                for stat in stats:
                    if stat['type'] == 'Ball Possession':
                        value = int(stat['value'].replace('%', '')) if stat['value'] else 50
                        posesion.append(value)
                    if stat['type'] == 'Shots on Goal':
                        tiros_meta.append(int(stat['value']) if stat['value'] else 0)
        
        # Calcular promedios
        avg_favor = sum(goles_favor) / len(goles_favor) if goles_favor else 1.2
        avg_contra = sum(goles_contra) / len(goles_contra) if goles_contra else 1.2
        avg_pos = sum(posesion) / len(posesion) if posesion else 50
        avg_tiros = sum(tiros_meta) / len(tiros_meta) if tiros_meta else 4
        
        return {
            "attack_power": avg_favor,
            "defense_weakness": avg_contra,
            "posesion": avg_pos,
            "tiros_meta": avg_tiros,
            "partidos_analizados": len(goles_favor)
        }
        
    except Exception as e:
        st.error(f"Error obteniendo stats: {e}")
        # Fallback a valores por defecto pero con advertencia
        return {
            "attack_power": 1.2,
            "defense_weakness": 1.2,
            "posesion": 50,
            "tiros_meta": 4,
            "partidos_analizados": 0,
            "error": str(e)
        }

def simular_probabilidades(stats_h, stats_a):
    """Wrapper que usa montecarlo.py con stats reales"""
    # Preparar stats en formato que espera montecarlo.py
    stats = {
        "home": {
            "attack": stats_h.get("attack_power", 50) * 10,  # Convertir a escala 0-100
            "defense": stats_h.get("defense_weakness", 50) * 10
        },
        "away": {
            "attack": stats_a.get("attack_power", 50) * 10,
            "defense": stats_a.get("defense_weakness", 50) * 10
        }
    }
    
    # Ejecutar Monte Carlo
    resultados = run_simulations(stats)
    
    return resultados