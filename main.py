import streamlit as st
import json
import os
import sys
import pandas as pd

# Configuración de rutas
current_dir = os.path.dirname(__file__)
modules_path = os.path.join(current_dir, 'modules')
if modules_path not in sys.path:
    sys.path.append(modules_path)

from vision_reader import analyze_betting_image
from tracker import guardar_pick_automatico

st.set_page_config(page_title="Ticket Pro IA", layout="wide")

tab1, tab2 = st.tabs(["🔥 Scanner", "📜 Historial"])

with tab1:
    st.title("🏀 Ticket Pro IA")
    archivo = st.file_uploader("Sube captura", type=['png', 'jpg', 'jpeg'])

    if archivo:
        st.image(archivo, width=500)
        if st.button("🚀 Analizar Mercados"):
            with st.spinner("Leyendo..."):
                res = analyze_betting_image(archivo)
                try:
                    juegos = json.loads(res)
                    for j in juegos:
                        with st.expander(f"📌 {j.get('away')} @ {j.get('home')}"):
                            st.write(f"Línea: {j.get('handicap')} | Momio: {j.get('moneyline')}")
                            guardar_pick_automatico(j, 0.05, 100.0)
                    st.success("Análisis completado")
                except:
                    st.error("La IA no devolvió un formato válido.")
                    st.code(res)

with tab2:
    if os.path.exists("data/picks.csv"):
        st.dataframe(pd.read_csv("data/picks.csv"))
    else:
        st.info("Historial vacío.")


