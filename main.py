import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Auditor de Élite 85%", layout="wide")
engine = EVEngine(threshold=0.85)

st.title("🛡️ Auditoría de Valor: Filtro 85%")

archivo = st.file_uploader("Cargar Ticket", type=["png", "jpg", "jpeg"])

if archivo:
    matches, _ = analyze_betting_image(archivo)
    
    for m in matches:
        res = engine.get_raw_probabilities(m)
        
        if res['status'] == "APROBADO":
            with st.container():
                st.markdown(f"""
                <div style="background:#1a2c3d; padding:20px; border-radius:10px; border-left:5px solid #2ecc71; margin-bottom:15px;">
                    <h3 style="margin:0;">Partido: {res['home']} vs {res['away']}</h3>
                    <p style="color:#2ecc71; font-size:1.3rem; margin:10px 0;"><b>Mejor opción: {res['pick_final']}</b></p>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size:0.9rem; color:#BDC3C7;">
                        <div>Probabilidad Poisson: <b>{res['prob_final']}%</b></div>
                        <div>Momio Ref: <b>{res['cuota_ref']}</b></div>
                        <div>EV: <b>{res['ev']}</b></div>
                        <div>λL: {res['lh']} | λV: {res['lv']} | Exp: {res['exp']}</div>
                    </div>
                    <p style="margin-top:10px; color:#2ecc71;"><b>Confianza: 🔥 EXCELENTE (supera 85%)</b></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#262730; padding:15px; border-radius:10px; border-left:5px solid #e74c3c; margin-bottom:10px; color:#BDC3C7;">
                Partido: {res['home']} vs {res['away']} → <b>Descartado – Ninguna opción supera el 85%</b>
            </div>
            """, unsafe_allow_html=True)

