import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Auditor de Élite 85%", layout="wide")
engine = EVEngine(threshold=0.85)

st.title("🛡️ Auditoría Betting AI: Filtro 85% (Cascada)")

archivo = st.file_uploader("Subir captura de ticket", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Motor de Visión analizando imagen real..."):
        matches, msg = analyze_betting_image(archivo)
    
    st.sidebar.success(msg)
    
    for m in matches:
        res = engine.get_raw_probabilities(m)
        
        if res['status'] == "APROBADO":
            st.markdown(f"""
            <div style="background:#1a2c3d; padding:20px; border-radius:12px; border-left:6px solid #2ecc71; margin-bottom:20px;">
                <h3 style="margin:0; color:white;">{res['home']} vs {res['away']}</h3>
                <p style="color:#2ecc71; font-size:1.4rem; margin:10px 0;"><b>Pick: {res['pick_final']}</b></p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 15px; color:#BDC3C7;">
                    <div>Probabilidad Real: <b>{res['prob_final']}%</b></div>
                    <div>Momio: <b>{res['cuota_ref']}</b></div>
                    <div>EV: <b>{res['ev']}</b> | Edge: <b>+{res['edge']}%</b></div>
                    <div>λL: {res['lh']} | λV: {res['lv']} | Exp: {res['exp']}</div>
                </div>
                <p style="margin-top:10px; color:#2ecc71;"><b>Confianza: 🔥 EXCELENTE (supera 85%)</b></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#262730; padding:15px; border-radius:10px; border-left:4px solid #e74c3c; margin-bottom:10px; color:#888;">
                Partido: {res['home']} vs {res['away']} → <span style="color:#e74c3c;"><b>Descartado</b></span> – Ninguna opción supera el 85%.
            </div>
            """, unsafe_allow_html=True)

