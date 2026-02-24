import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Ticket Pro IA", layout="wide")

# Inicialización segura para evitar KeyError
try:
    if "engine" not in st.session_state:
        st.session_state.engine = EVEngine(
            st.secrets["GOOGLE_API_KEY"], 
            st.secrets["GOOGLE_CSE_ID"]
        )
except KeyError as e:
    st.error(f"❌ Error de configuración: Falta la llave {e} en los Secrets de Streamlit.")
    st.stop()

