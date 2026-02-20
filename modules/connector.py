import streamlit as st
import requests

def obtener_datos_caliente_limpios():
    # Usamos la API para traer Totales y Puntos de Jugadores
    API_KEY = st.secrets["ODDS_API_KEY"]
    base_url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/"
    
    # Parámetros para buscar mercados de jugadores y totales
    params = {
        'apiKey': API_KEY,
        'regions': 'us',
        'markets': 'totals,player_points', 
        'oddsFormat': 'american'
    }
    
    try:
        response = requests.get(base_url, params=params).json()
        partidos_procesados = []
        
        for game in response:
            home = game['home_team']
            away = game['away_team']
            
            # Filtro para evitar momios basura como -1000
            bookmaker = game['bookmakers'][0]
            market = bookmaker['markets'][0]
            
            # Extraemos la línea (ej. 228.5 o 25.5 de un jugador)
            linea = market['outcomes'][0]['point']
            momio = market['outcomes'][0]['price']
            
            if -500 < momio < 500: # Filtro de seguridad profesional
                partidos_procesados.append({
                    "game": f"{away} @ {home}",
                    "home": home,
                    "away": away,
                    "linea": linea,
                    "momio": momio,
                    "tipo_mercado": market['key']
                })
        return partidos_procesados
    except Exception as e:
        st.error(f"Error en API: {e}")
        return []

