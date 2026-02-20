import streamlit as st
import requests

def obtener_datos_caliente_limpios():
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    # Usamos 'totals' para obtener el Over/Under como en tu imagen
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=totals"
    
    response = requests.get(url).json()
    partidos_limpios = []
    
    for game in response:
        try:
            # Extraemos la línea de puntos (ej: 231 para Cavs vs Hornets)
            bookmaker = game['bookmakers'][0]
            market = bookmaker['markets'][0]
            linea = market['outcomes'][0]['point']
            momio = market['outcomes'][0]['price']
            
            # FILTRO DE SEGURIDAD PARA MOMIOS EXTRAÑOS
            # Si el momio es muy extremo, lo ignoramos para evitar errores de cálculo
            if momio > 5.0 or momio < 1.2: 
                continue

            partidos_limpios.append({
                "home": game['home_team'],
                "away": game['away_team'],
                "linea": linea,
                "momio": momio
            })
        except:
            continue
    return partidos_limpios
