import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.cerebro import CerebroAuditor # Asumiendo tu clase Cerebro

st.set_page_config(page_title="Auditoría Pro", layout="wide")
engine = EVEngine(threshold=0.85)
auditor = CerebroAuditor()

st.title("🛡️ Sistema de Auditoría Total 85%")

archivo = st.file_uploader("Subir Captura", type=["jpg", "png", "jpeg"])

if archivo:
    st.image(archivo, width=250)
    with st.spinner("Analizando con Google Vision..."):
        games = analyze_betting_image(archivo)
        
    if games:
        for g in games:
            res_math = engine.get_probabilities(g)
            if res_math:
                # El Cerebro le da el toque final
                veredicto = auditor.decidir_mejor_apuesta(res_math, "Neutral", {})
                
                st.markdown(f"""
                <div style="background:#1a2c3d; padding:15px; border-radius:10px; border-left:5px solid #00ff9d; margin-bottom:10px;">
                    <h4>{g['home']} vs {g['away']}</h4>
                    <p style="color:#00ff9d;"><b>PICK: {veredicto['pick_final']}</b></p>
                    <p>Confianza: {veredicto['confianza_final']}% | Cuota: {res_math['c']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"🚫 {g['home']} vs {g['away']}: Sin picks seguros (Prob < 85%)")
