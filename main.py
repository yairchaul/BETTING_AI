import streamlit as st
import sys
import os

# FIX STREAMLIT CLOUD IMPORTS
sys.path.append(os.path.dirname(__file__))

from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Parlay Maestro IA",
    layout="wide"
)

st.title("🎯 Parlay Maestro IA — SaaS V3")

# ---------------- SECRETS VALIDATION ----------------

required_secrets = ["GOOGLE_API_KEY", "GOOGLE_CSE_ID"]

for secret in required_secrets:
    if secret not in st.secrets:
        st.error(f"❌ Falta el secret: {secret}")
        st.stop()

# ---------------- FILE UPLOAD ----------------

archivo = st.file_uploader(
    "Sube la captura de tus momios",
    type=["png", "jpg", "jpeg"]
)

if archivo:

    st.image(archivo, caption="Captura cargada", width=400)

    if st.button("🚀 INICIAR ANÁLISIS"):

        with st.spinner("🤖 Analizando apuestas..."):

            equipos = analyze_betting_image(archivo)

            if not equipos or len(equipos) < 2:
                st.warning("⚠️ No se detectaron suficientes equipos.")
                st.stop()

            engine = EVEngine(
                st.secrets["GOOGLE_API_KEY"],
                st.secrets["GOOGLE_CSE_ID"]
            )

            resultados, parlay = engine.analyze_matches(equipos)

            # -------- RESULTADOS --------

            st.subheader("📊 Resultados del Análisis")

            for p in resultados:

                prob = p.probabilidad

                if prob >= 75:
                    color, emo = "#28a745", "🔥"
                elif prob >= 55:
                    color, emo = "#ffc107", "⚖️"
                else:
                    color, emo = "#dc3545", "⚠️"

                st.markdown(f"""
                <div style="
                    border-left:6px solid {color};
                    padding:15px;
                    background:#1e1e1e;
                    margin-bottom:10px;
                    border-radius:8px;
                ">
                    {emo} <b>{p.partido}</b><br>
                    Pick: <span style="color:{color};">
                    {p.pick}</span><br>
                    Confianza: <b>{prob}%</b>
                </div>
                """, unsafe_allow_html=True)

            # -------- PARLAY --------

            if parlay:
                st.success(
                    f"✅ Parlay recomendado con {len(parlay)} selecciones."
                )

engine = EVEngine()

for i in range(0, len(equipos), 2):

    local = equipos[i]
    visitante = equipos[i+1]

    pick, prob = engine.cascade_pick(local, visitante)
