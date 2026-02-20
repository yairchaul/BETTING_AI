import requests
from config import ODDS_API_KEY, SPORT, REGION, MARKET

def obtener_juegos():

    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal"
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        print("[API ERROR]", r.status_code)
        return []

    data = r.json()

    juegos = []

    for game in data:
        try:
            linea = game["bookmakers"][0]["markets"][0]["outcomes"][0]["point"]

            juegos.append({
                "home": game["home_team"],
                "away": game["away_team"],
                "line": linea
            })
        except:
            continue

    return juegos