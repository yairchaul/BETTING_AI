import requests
import streamlit as st

API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["GOOGLE_CSE_ID"]


def get_match_context(home, away):

    query = f"{home} vs {away} injuries lineup news"

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "num": 3
    }

    try:
        r = requests.get(url, params=params).json()

        snippets = [
            item["snippet"]
            for item in r.get("items", [])
        ]

        return " ".join(snippets).lower()

    except:
        return ""
