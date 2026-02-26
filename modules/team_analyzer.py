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

    context = google_search(
        f"{team} football stats goals per game corners possession attacking defensive style"
    )

    attack = 1.2
    defense = 1.2
    pace = 1.2
    corners = 5.0

    if "attacking" in context:
        attack += 0.4

    if "defensive" in context:
        defense += 0.3

    if "fast" in context or "pressing" in context:
        pace += 0.3

    if "corner" in context:
        corners += 1.5

    return {
        "attack": attack,
        "defense": defense,
        "pace": pace,
        "corners": corners,
    }
