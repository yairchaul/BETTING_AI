import streamlit as st
import pandas as pd
import os
import glob
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Auditoría Élite 85%", layout="wide")
engine = EVEngine(threshold=0.85)

# --- BÚSQUEDA PROFUNDA DE HISTORIAL ---
def localizar_historial():
    # Buscamos en todas las subcarpetas archivos que se llamen historial o tracker
    archivos = glob.glob("**/*.csv", recursive=True)
    for f in archivos:
        if "historial" in f.lower() or "tracker" in f.lower():
            return f
    return None

path_historial = localizar_historial()

st.title("🛡️ Auditoría Betting AI: Filtro 85%")

archivo = st.file_uploader("Subir imagen de momios", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Escaneando con Vision AI..."):
        matches, msg = analyze_betting_image(archivo)
    st.sidebar.info(msg)

    if matches:
        for m in matches:
            res = engine.get_raw_probabilities(m)
            # APLICACIÓN DE TU MODELO CASCADA
            if res['status'] == "APROBADO":
                st.markdown(f"""
                <div style="background:#1a2c3d; padding:20px; border-radius:10px; border-left:6px solid #2ecc71; margin-bottom:15px;">
                    <h3>{res['home']} vs {res['away']}</h3>
                    <p style="color:#2ecc71; font-size:1.3rem;"><b>Pick Sugerido: {res['pick']}</b></p>
                    <p>Probabilidad: {res['prob']}% | Cuota: {res['cuota']} | EV: {res['ev']}</p>
                    <small style="color:#888;">λL: {res['lh']} | λV: {res['lv']} | Exp: {res['exp']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write(f"🚫 {res['home']} vs {res['away']} → Descartado (<85%)")

# --- SECCIÓN DE HISTORIAL RECUPERADO ---
st.divider()
st.subheader("🏁 Historial de Apuestas Localizadas")

if path_historial:
    st.success(f"Archivo de datos encontrado: `{path_historial}`")
    df = pd.read_csv(path_historial)
    if not df.empty:
        # Formateo estricto: Cuotas y montos a 2 decimales, resto limpio
        cols_num = df.select_dtypes(include=['float64']).columns
        st.dataframe(
            df.style.format({col: "{:.2f}" for col in cols_num}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("El archivo está vacío. Registra nuevos picks para verlo crecer.")
else:
    st.warning("No se encontró historial previo. El sistema creará uno nuevo al guardar tu primer pick.")
