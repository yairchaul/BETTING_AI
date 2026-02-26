import streamlit as st
import requests

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]


def google_search(query):

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        return ""

    data = r.json()

    text = ""

    for item in data.get("items", []):
        text += item.get("snippet", "") + " "

    return text.lower()


def build_team_profile(team):

    query = f"{team} football team stats goals per game corners possession shots"

    context = google_search(query)

    # defaults neutrales
    attack = 1.3
    defense = 1.3
    pace = 1.3
    corners = 5

    if "high scoring" in context or "attacking" in context:
        attack += 0.3

    if "defensive" in context:
        defense += 0.3

    if "fast" in context or "high tempo" in context:
        pace += 0.3

    if "many corners" in context:
        corners += 1.5

    return {
        "attack": attack,
        "defense": defense,
        "pace": pace,
        "corners": corners,
    }
