import json
import os
import streamlit as st

DB_FILE = "betting_history.json"

def save_parlay(data):
    history = get_history()
    history.append(data)
    with open(DB_FILE, "w") as f:
        json.dump(history, f, indent=4)
    # Forzar actualización en Streamlit
    st.session_state['last_update'] = data['fecha']

def get_history():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []
