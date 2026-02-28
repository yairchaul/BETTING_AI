import requests
import os
from datetime import datetime

API_KEY = os.getenv("API_FOOTBALL_KEY")  # o st.secrets["API_FOOTBALL_KEY"] en Streamlit

def get_team_stats(home, away, league_id=140):  # 140=LaLiga, cambia por liga
    url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"
    headers = {"X-RapidAPI-Key": API_KEY}
    
    # Busca IDs de equipos (simplificado; añade búsqueda si nombres varían)
    team_ids = get_team_ids(home, away)  # Implementa esto: API /teams?search=home
    if not team_ids:
        return {"home": {"attack": 50, "defense": 50}, "away": {"attack": 50, "defense": 50}}  # Fallback
    
    stats = {}
    for team, tid in [("home", team_ids["home"]), ("away", team_ids["away"])]:
        params = {"league": league_id, "season": datetime.now().year - 1, "team": tid}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()["response"]
            goals_for = data["goals"]["for"]["average"]["total"]
            goals_against = data["goals"]["against"]["average"]["total"]
            stats[team] = {"attack": goals_for * 25, "defense": 100 - (goals_against * 25)}  # Normaliza a 0-100
        else:
            stats[team] = {"attack": 50, "defense": 50}
    
    return stats

def get_team_ids(home, away):
    # Implementa búsqueda real via /teams?search=
    # Por ahora, hardcodea para pruebas o usa web_search si necesitas
    return {"home": 123, "away": 456}  # Reemplaza con IDs reales de API