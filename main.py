# main.py - Auditor de Valor IA - Fútbol
import streamlit as st   # ← ESTA LÍNEA ES LA QUE FALTABA
import pandas as pd
import re

# Importa tus módulos (ajusta según lo que tengas)
from modules.vision_reader import analizar_ticket
from modules.ev_engine import EVEngine
# ... otros imports que ya tenías (autopicks, bankroll, etc.)

# Configuración de página
st.set_page_config(page_title="Auditor de Valor IA", layout="wide")

# Estilo tarjetas azules (mantén tu estética)
st.markdown("""
    <style>
        .card { 
            background:#1a2c3d; 
            padding:20px; 
            border-left:5px solid #1E88E5; 
            border-radius:10px; 
            margin-bottom:15px; 
        }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 Auditor de Valor IA - Fútbol")

engine = EVEngine()

# Sección de carga (aquí estaba el error)
st.subheader("Analizar ticket (sube imagen o pega texto)")
col1, col2 = st.columns(2)

with col1:
    archivo = st.file_uploader("Sube captura del ticket", type=["png", "jpg", "jpeg"])

with col2:
    texto_manual = st.text_area("O pega el texto del ticket aquí", height=150)

# Procesar cuando haya input
if archivo is not None or texto_manual:
    matches, mensaje = analizar_ticket(archivo=archivo, texto_manual=texto_manual)
    st.write(mensaje)
    
    if matches:
        for partido in matches:
            resultado = engine.analizar_partido(partido)
            if resultado:
                st.markdown(f"""
                <div class="card">
                    <h3>{resultado.get('home', 'Equipo A')} vs {resultado.get('away', 'Equipo B')}</h3>
                    <p><strong>Mejor opción:</strong> {resultado.get('mejor_pick', 'Pendiente')}</p>
                    <p>Probabilidad: {resultado.get('prob', 0)}% | EV: {resultado.get('ev', 0)}</p>
                    <small>λ Home: {resultado.get('λ_home', 0)} | λ Away: {resultado.get('λ_away', 0)} | Edge: {resultado.get('edge', 0)}%</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No se detectaron partidos válidos en la imagen o texto.")
