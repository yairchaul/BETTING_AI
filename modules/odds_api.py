import requests
import os

API_KEY = os.getenv("THE_ODDS_API_KEY")

def fetch_odds(home, away, sport="soccer_laliga"):  # Ajusta sport por liga
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {"apiKey": API_KEY, "regions": "us,eu", "markets": "h2h,totals,halftime_totals"}  # Añade mercados que quieres
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # Filtra por partido (busca home/away en outcomes)
        for game in data:
            if game["home_team"].lower() in home.lower() and game["away_team"].lower() in away.lower():
                return parse_odds(game)  # Devuelve dict con odds por mercado
    return {}  # Fallback vacío

def parse_odds(game):
    odds = {}
    for bookmaker in game["bookmakers"]:
        for market in bookmaker["markets"]:
            if market["key"] == "h2h":
                outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                odds["Resultado Final (Local)"] = outcomes.get(home, 0)
                odds["Resultado Final (Empate)"] = outcomes.get("Draw", 0)
                odds["Resultado Final (Visitante)"] = outcomes.get(away, 0)
            elif market["key"] == "totals":
                # Over/Under, ajusta thresholds 1.5,2.5,3.5
                pass  # Expande para tus mercados
            # Añade para BTTS (both teams score), halftime, combos
    return odds