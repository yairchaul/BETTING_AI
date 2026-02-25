import streamlit as st
import pandas as pd
import os
import glob
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Betting AI - Auditoría 85%", layout="wide")
engine = EVEngine(threshold=0.85)

# --- ESCÁNER DE HISTORIAL ---
def buscar_historial():
    # Busca cualquier archivo CSV que pueda contener el historial
    posibles = glob.glob("**/historial*.csv", recursive=True) + glob.glob("**/tracker*.csv", recursive=True)
    return posibles[0] if posibles else None

path_historial = buscar_historial()

st.title("🛡️ Auditoría Betting AI: Filtro 85%")

# Análisis de Imagen
archivo = st.file_uploader("Subir imagen de momios", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Escaneando imagen con Vision AI..."):
        matches, msg = analyze_betting_image(archivo)
    st.sidebar.info(msg)

    if matches:
        for m in matches:
            res = engine.get_raw_probabilities(m)
            if res['status'] == "APROBADO":
                st.markdown(f"""
                <div style="background:#1a2c3d; padding:20px; border-radius:10px; border-left:6px solid #2ecc71; margin-bottom:15px;">
                    <h3 style="margin:0;">{res['home']} vs {res['away']}</h3>
                    <p style="color:#2ecc71; font-size:1.3rem;"><b>Sugerencia: {res['pick']}</b></p>
                    <p>Probabilidad: {res['prob']}% | Cuota: {res['cuota']} | EV: {res['ev']}</p>
                    <small style="color:#888;">Razones: λL: {res['lh']} | λV: {res['lv']} | Goles Exp: {res['exp']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write(f"🚫 {res['home']} vs {res['away']} → Descartado (<85%)")

# --- VISUALIZACIÓN DE DATOS RECUPERADOS ---
st.divider()
st.subheader("🏁 Historial de Apuestas Localizadas")

if path_historial:
    st.caption(f"Archivo localizado en: `{path_historial}`")
    df = pd.read_csv(path_historial)
    if not df.empty:
        # Formateo estricto para evitar ceros basura (.000000)
        # Identificamos columnas numéricas para redondear a 2 decimales
        cols_num = df.select_dtypes(include=['float64', 'int64']).columns
        st.dataframe(
            df.style.format({col: "{:.2f}" for col in cols_num}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("El archivo está vacío.")
else:
    st.warning("No se encontró ningún archivo de historial (.csv) en el proyecto.")
