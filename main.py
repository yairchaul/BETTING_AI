import streamlit as st

from modules.vision_reader import analyze_betting_image
from modules.ev_engine import analyze_matches


# ======================
# CONFIG UI
# ======================

st.set_page_config(layout="wide")

st.title("🧠 EV ELITE v4 — Sharp Money Detector")


# ======================
# SUBIR TICKET
# ======================

uploaded = st.file_uploader(
    "Sube tu ticket de apuestas",
    type=["png", "jpg", "jpeg"]
)

# ======================
# ANALISIS
# ======================

if uploaded:

    games = analyze_betting_image(uploaded)

    if not games:
        st.error("❌ No se detectaron partidos")
        st.stop()

    st.subheader("📋 Partidos Detectados")
    st.dataframe(games)

    # ======================
    # ANALISIS IA
    # ======================

    results = analyze_matches(games)

    if not results:
        st.warning("⚠️ Ningún pick con EV positivo")
        st.stop()

    st.divider()
    st.subheader("🔥 Picks Sharp Detectados")

    total_ev = 0

    for r in results:

        st.success(
            f"🎯 {r.match}\n"
            f"Sugerido: {r.selection}\n"
            f"Probabilidad: {r.probability}\n"
            f"EV: {r.ev}"
        )

        total_ev += r.ev

    st.divider()

    col1, col2 = st.columns(2)

    col1.metric("Picks Totales", len(results))
    col2.metric("EV Total", round(total_ev, 3))
