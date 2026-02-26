import requests
import streamlit as st
import random


def build_team_profile(team_name):

    # ======================
    # GOOGLE INTELLIGENCE
    # ======================

    api = st.secrets["GOOGLE_API_KEY"]
    cx = st.secrets["GOOGLE_CSE_ID"]

    query = f"{team_name} football team statistics goals scored corners form"

    try:

        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            "key": api,
            "cx": cx,
            "q": query
        }

        r = requests.get(url, params=params, timeout=4)
        data = r.json()

        text_blob = " ".join(
            item["snippet"]
            for item in data.get("items", [])
        ).lower()

        attack = 1.2
        corners = 5.5

        if "attacking" in text_blob:
            attack += 0.2

        if "defensive" in text_blob:
            attack -= 0.15

        if "corner" in text_blob:
            corners += 1

    except:
        attack = random.uniform(1.0, 1.5)
        corners = random.uniform(4.5, 6.5)

    return {
        "attack": attack,
        "corners": corners
    }
