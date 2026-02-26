import requests
import streamlit as st


def get_market_odds(home, away):

    key = st.secrets["ODDS_API_KEY"]

    try:

        url = "https://api.the-odds-api.com/v4/sports/soccer/odds"

        params = {
            "apiKey": key,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }

        r = requests.get(url, params=params, timeout=6)
        data = r.json()

        for game in data:

            teams = game.get("teams", [])

            if home in teams and away in teams:

                bookmakers = game["bookmakers"][0]
                outcomes = bookmakers["markets"][0]["outcomes"]

                odds = {}
                for o in outcomes:
                    odds[o["name"]] = o["price"]

                return odds

    except:
        return None

    return None
