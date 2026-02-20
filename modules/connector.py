import streamlit as st
import requests

def obtener_datos_caliente_limpios():
    API_KEY = st.secrets["ODDS_API_KEY"]
    base_url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/"
    
    # Solicitamos múltiples mercados para tener de donde elegir
    params = {
        'apiKey': API_KEY,
        'regions': 'us',
        'markets': 'totals,h2h,player_points', 
        'oddsFormat': 'american'
    }
    
    try:
        response = requests.get(base_url, params=params).json()
        if not isinstance(response, list): # Verificación de seguridad para evitar el error de la imagen
            return []
            
        partidos_procesados = []
        for game in response:
            data_partido = {
                "id": game['id'],
                "game": f"{game['away_team']} @ {game['home_team']}",
                "home": game['home_team'],
                "away": game['away_team'],
                "mercados": {}
            }
            
            # Organizamos los mercados disponibles
            for bookmaker in game.get('bookmakers', []):
                if bookmaker['key'] == 'draftkings' or bookmaker['key'] == 'betonlineag':
                    for market in bookmaker.get('markets', []):
                        data_partido["mercados"][market['key']] = market['outcomes']
            
            partidos_procesados.append(data_partido)
        return partidos_procesados
    except Exception as e:
        st.error(f"Error en API: {e}")
        return []

