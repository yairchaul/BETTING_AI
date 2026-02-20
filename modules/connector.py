import requests
import streamlit as st

def obtener_juegos():
    # --- CONFIGURACIÓN DESDE SECRETS ---
    # Sustituimos el archivo config por st.secrets
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    SPORT = "basketball_nba" # O la variable que uses
    REGION = "us"            # O 'eu' según tu preferencia
    MARKET = "h2h"           # O 'spreads' / 'totals'

    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal"
    }

    try:
        r = requests.get(url, params=params)
        
        if r.status_code != 200:
            st.error(f"Error de API: {r.status_code}")
            return []

        data = r.json()
        juegos = []

        for game in data:
            try:
                # Extraemos la línea o momio base
                # Nota: Ajustamos la ruta según la respuesta de The Odds API
                linea = game["bookmakers"][0]["markets"][0]["outcomes"][0].get("point", 0)

                juegos.append({
                    "game": f"{game['away_team']} @ {game['home_team']}",
                    "jugador": "Varios", # The Odds API h2h no da jugadores por defecto
                    "linea": linea,
                    "prob_modelo": 0.55, # Aquí conectarás tu lógica de ev_engine.py
                    "momio_caliente": -110
                })
            except (IndexError, KeyError):
                continue

        return juegos
    except Exception as e:
        st.error(f"Error en la conexión: {e}")
        return []

    return juegos
