import streamlit as st
import os
from modules.vision_reader import read_ticket_image
from modules.ev_engine import analyze_matches, build_smart_parlay

st.set_page_config(page_title="BETTING AI EV+", layout="wide")

st.title("🧠 BETTING AI — Sharp Money Detector")

uploaded = st.file_uploader("Sube imagen del ticket", type=["png", "jpg", "jpeg"])

if uploaded:
    with st.spinner("Analizando y procesando últimos 5 partidos..."):
        # 1. OCR
        games = read_ticket_image(uploaded)
        
        if not games:
            st.error("No se detectaron partidos.")
        else:
            # 2. Análisis
            results = analyze_matches(games)

            if not results:
                st.warning("Sin oportunidades EV+ encontradas.")
            else:
                st.subheader("🔥 Picks Sharp Detectados")
                for res in results:
                    r = res["pick"]
                    with st.expander(f"📍 {r.match} | {r.selection}", expanded=True):
                        st.metric("EV", f"{round(r.ev * 100, 1)}%", delta=f"{r.odd} cuota")
                        st.text("Probabilidades calculadas:")
                        st.code(res["text"])

                # 3. Parlay de 5 picks
                st.divider()
                lista_picks = [res["pick"] for res in results]
                parlay = build_smart_parlay(lista_picks)

                if parlay:
                    st.subheader("🚀 Smart Parlay Sugerido (Top 5)")
                    with st.container(border=True):
                        st.write(f"**Combinada:** {' + '.join(parlay.matches)}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Cuota Total", f"{parlay.total_odd}x")
                        c2.metric("Probabilidad", f"{round(parlay.combined_prob * 100, 1)}%")
                        c3.metric("EV Total", f"{parlay.total_ev}")

                        st.divider()
                        monto = st.number_input("Monto a invertir ($)", min_value=10.0, value=100.0)
                        st.success(f"💰 **Ganancia Posible: ${round(monto * parlay.total_odd, 2)}**")

