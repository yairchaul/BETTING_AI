import streamlit as st
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración de página
st.set_page_config(page_title="Auditor de Valor 85%", layout="wide")
engine = EVEngine(threshold=0.85)

st.title("🛡️ Auditoría Betting AI: Filtro 85%")

archivo = st.file_uploader("Subir imagen de momios", type=["png", "jpg", "jpeg"])

if archivo:
    # Mostramos un spinner para que el usuario sepa que se está procesando su imagen
    with st.spinner("Analizando tu imagen con Vision AI..."):
        matches, debug_msg = analyze_betting_image(archivo)
    
    st.sidebar.markdown(f"### Estatus del Lector\n{debug_msg}")

    if not matches:
        st.error("No se pudieron detectar partidos. Asegúrate de que los momios sean visibles.")
    else:
        for m in matches:
            res = engine.get_raw_probabilities(m)
            
            if res['status'] == "APROBADO":
                st.markdown(f"""
                <div style="background:#1a2c3d; padding:20px; border-radius:10px; border-left:6px solid #2ecc71; margin-bottom:15px;">
                    <h3 style="margin:0;">Partido: {res['home']} vs {res['away']}</h3>
                    <p style="color:#2ecc71; font-size:1.3rem; margin:10px 0;"><b>Opción Sugerida: {res['pick']}</b></p>
                    <p style="font-size:0.9rem; color:#BDC3C7;">
                        Probabilidad: {res['prob']}% | Cuota: {res['cuota']} | EV: {res['ev']}<br>
                        Técnico: λL {res['lh']} | λV {res['lv']} | Goles Exp: {res['exp']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#262730; padding:10px; border-radius:8px; border-left:4px solid #e74c3c; margin-bottom:10px; color:#888;">
                    Partido: {res['home']} vs {res['away']} → <span style="color:#e74c3c;">Descartado (No supera el 85%)</span>
                </div>
                """, unsafe_allow_html=True)
