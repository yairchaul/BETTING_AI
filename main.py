import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Auditor de Élite 85%", layout="wide")
engine = EVEngine(threshold=0.85)

st.title("🛡️ Auditoría Betting AI: Filtro 85%")

archivo = st.file_uploader("Subir captura de ticket (Carga Global)", type=["png", "jpg", "jpeg"])

# En main.py
if archivo:
    # AQUÍ PASAMOS EL ARCHIVO REAL
    matches, debug_msg = analyze_betting_image(archivo) 
    st.sidebar.info(debug_msg)
    
    if not matches:
        st.warning("El lector no pudo encontrar datos en esta imagen. Intenta con otra captura.")
    else:
        # Proceder con el filtro 85%...


if archivo:
    matches, debug_msg = analyze_betting_image(archivo)
    st.sidebar.info(debug_msg)
    
    for m in matches:
        res = engine.get_raw_probabilities(m)
        
        if res['status'] == "APROBADO":
            st.markdown(f"""
            <div style="background:#1a2c3d; padding:20px; border-radius:12px; border-left:6px solid #2ecc71; margin-bottom:20px;">
                <h3 style="margin:0; color:white;">Partido: {res['home']} vs {res['away']}</h3>
                <p style="color:#2ecc71; font-size:1.4rem; margin:10px 0;"><b>Mejor opción seleccionada: {res['pick_final']}</b></p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 15px; color:#BDC3C7;">
                    <div>Probabilidad Poisson: <b>{res['prob_final']}%</b></div>
                    <div>Momio disponible: <b>{res['cuota_ref']}</b></div>
                    <div>EV: <b>{res['ev']}</b></div>
                    <div>Edge: <b>+{res['edge']}%</b></div>
                </div>
                <div style="margin-top:15px; font-size:0.85rem; color:#888;">
                    Razones técnicas: λL: {res['lh']} | λV: {res['lv']} | Goles esperados: {res['exp']}
                </div>
                <p style="margin-top:10px; color:#2ecc71; font-weight:bold;">Confianza: 🔥 EXCELENTE (supera 85%)</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#262730; padding:15px; border-radius:10px; border-left:4px solid #e74c3c; margin-bottom:10px; color:#888;">
                Partido: {res['home']} vs {res['away']} → <span style="color:#e74c3c;"><b>Descartado</b></span> – Ninguna opción supera el 85% de probabilidad real.
            </div>
            """, unsafe_allow_html=True)


