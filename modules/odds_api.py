import requests
import streamlit as st

ODDS_API_KEY = st.secrets["ODDS_API_KEY"]

BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer/odds"


def get_market_odds(home, away):

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h,totals",
        "oddsFormat": "decimal"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        games = response.json()

        for game in games:

            if home.lower() in game["home_team"].lower() \
            or away.lower() in game["away_team"].lower():

                bookmakers = game["bookmakers"][0]
                markets = bookmakers["markets"]

                odds = {}

                for m in markets:

                    if m["key"] == "h2h":
                        for o in m["outcomes"]:
                            odds[o["name"]] = o["price"]

                    if m["key"] == "totals":
                        for o in m["outcomes"]:
                            if o["name"] == "Over":
                                odds[f"OVER_{o['point']}"] = o["price"]

                return odds

    except Exception as e:
        print("ODDS API ERROR:", e)

    return {}
