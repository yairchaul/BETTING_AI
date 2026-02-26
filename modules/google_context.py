import requests
import streamlit as st


def get_match_context(home, away):

    api = st.secrets["GOOGLE_API_KEY"]
    cx = st.secrets["GOOGLE_CSE_ID"]

    query = f"{home} vs {away} injuries suspension lineup news"

    try:

        url = "https://www.googleapis.com/customsearch/v1"

        r = requests.get(url, params={
            "key": api,
            "cx": cx,
            "q": query
        }, timeout=4)

        data = r.json()

        text = " ".join(
            item["snippet"]
            for item in data.get("items", [])
        ).lower()

        signals = []

        if "injury" in text:
            signals.append("injury")

        if "rotation" in text:
            signals.append("rotation")

        if "missing" in text:
            signals.append("missing_players")

        return signals

    except:
        return []
