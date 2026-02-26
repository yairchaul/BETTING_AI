import streamlit as st
import requests

ODDS_API_KEY = st.secrets["ODDS_API_KEY"]

def get_market_odds(home, away):

    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h,totals",
        "oddsFormat": "decimal",
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        return None

    data = r.json()

    for game in data:
        teams = game.get("teams", [])
        if home in teams or away in teams:
            return {"market_found": True}

    return None
