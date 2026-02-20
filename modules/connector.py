import requests
import streamlit as st

def obtener_juegos_con_lineas():
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    # Cambiamos el mercado a 'totals' para ver los Overs
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "totals", # <--- CRÍTICO: Antes tenías 'h2h'
        "oddsFormat": "decimal"
    }
    
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
    r = requests.get(url, params=params)
    data = r.json()
    
    juegos_analizados = []
    for game in data:
        try:
            # Buscamos la línea de puntos (ej. 231)
            market = game["bookmakers"][0]["markets"][0]
            linea_puntos = market["outcomes"][0]["point"]
            
            # --- AQUÍ ENTRA TU LÓGICA DE ESTADÍSTICA ---
            # Simulamos que el motor analiza historial y tendencias
            # En el futuro, aquí llamarás a tu módulo 'ev_engine.py'
            prob_calculada = 0.65 if "Cleveland" in game["home_team"] else 0.51 
            
            juegos_analizados.append({
                "game": f"{game['away_team']} @ {game['home_team']}",
                "linea": linea_puntos,
                "prob_modelo": prob_calculada,
                "momio": market["outcomes"][0]["price"]
            })
        except:
            continue
    return juegos_analizados
