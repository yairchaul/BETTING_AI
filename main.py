import streamlit as st
import pandas as pd
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Betting AI Auditor", layout="wide")
engine = EVEngine()

st.title("🧠 Auditoría Analítica de Partidos")

archivo = st.file_uploader("Subir captura de momios", type=["png", "jpg", "jpeg"])

if archivo:
    matches, debug = analyze_betting_image(archivo)
    
    if matches:
        st.info(debug)
        cols = st.columns(2)
        for i, m in enumerate(matches):
            res = engine.get_raw_probabilities(m)
            
            with cols[i % 2]:
                # Tarjeta visual inspirada en la Imagen 11
                st.markdown(f"""
                <div style="background:#1a2c3d; padding:20px; border-radius:10px; border-left:5px solid #1E88E5; margin-bottom:15px;">
                    <h3 style="margin:0;">{res['home']} vs {res['away']}</h3>
                    <p style="color:#42A5F5; font-size:1.1rem; margin:10px 0;">🎯 <b>Pick: {res['pick_final']}</b></p>
                    <p style="font-size:0.9rem; color:#BDC3C7;">
                        Confianza: <b>{res['prob_final']}%</b> | Cuota: <b>{res['cuota_ref']}</b> | EV: <b>{res['ev_final']}</b><br>
                        <small>{res['tecnico']}</small>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
        # Sección de inversión con limpieza de decimales
        st.divider()
        inv = st.number_input("Inversión Total", value=100.0, step=50.0)
        # Aquí iría el registro al historial formateado a 2 decimales
    else:
        st.error("No se detectaron datos. Asegúrate de que los momios (+/-) sean visibles.")

