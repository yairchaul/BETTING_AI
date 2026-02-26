import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import build_parlay


st.set_page_config(layout="wide")

st.title("🔥 Análisis de la Mejor Opción")

uploaded = st.file_uploader("Sube ticket", type=["png","jpg","jpeg"])

if uploaded:

    games = analyze_betting_image(uploaded)

    st.subheader("📋 Verificación de Partidos")
    st.dataframe(games)

    results = build_parlay(games)

    if results:

        total_odd = 1

        for r in results:

            total_odd *= r.odd

            st.success(
                f"🎯 {r.match}\n"
                f"Sugerido: {r.selection} | "
                f"Cuota: x{r.odd} | "
                f"Prob: {r.probability}"
            )

        st.divider()

        stake = st.number_input("Inversión (MXN)", value=10.0)

        payout = stake * total_odd

        col1, col2, col3 = st.columns(3)

        col1.metric("Cuota Final", f"{total_odd:.2f}x")
        col2.metric("Pago Potencial", f"${payout:.2f}")
        col3.metric("Ganancia Neta", f"${payout-stake:.2f}")
