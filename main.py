import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración inicial segura
st.set_page_config(page_title="Ticket Pro IA", layout="wide")

# Inicializar motor con llaves ocultas
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    CSE_ID = st.secrets["GOOGLE_CSE_ID"]
    engine = EVEngine(API_KEY, CSE_ID)
except Exception as e:
    st.error("Error: Configura las llaves en los Secrets de Streamlit.")

st.title("🎯 Ticket Pro IA: Análisis Fútbol")

archivo = st.file_uploader("Sube tu captura de Caliente/Liga MX", type=['png', 'jpg', 'jpeg'])

if archivo:
    col_img, col_info = st.columns([1, 2])
    with col_img:
        st.image(archivo, width=280)
    
    with col_info:
        if st.button("🚀 Iniciar Análisis con Datos Reales"):
            # Lógica de análisis aquí...
            st.info("Buscando últimos 5 partidos en Google...")


