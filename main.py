import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Protección contra KeyError
try:
    if "engine" not in st.session_state:
        # Usamos los nombres exactos de tus secretos
        st.session_state.engine = EVEngine(
            st.secrets["GOOGLE_API_KEY"], 
            st.secrets["GOOGLE_CSE_ID"]
        )
except Exception as e:
    st.error(f"⚠️ Error de configuración: {e}")
    st.stop()
