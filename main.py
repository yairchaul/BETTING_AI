import streamlit as st
import pandas as pd
import datetime
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        hist = pd.read_csv("parlay_history.csv")
        st.metric("ROI Total", f"{(hist['ganancia_neta'].sum() / hist['monto'].sum() * 100):.1f}%")
        st.metric("Apostado", f"${hist['monto'].sum():.2f}")
    else:
        st.info("Aún no hay parlays registrados")

archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando imagen..."):
        games = analyze_betting_image(archivo)
    
    if games:
        # SECCIÓN COLAPSABLE (Oculta el debug por defecto)
        with st.expander("🏟️ Verificación de Partidos (Click para ver/ocultar)", expanded=False):
            st.dataframe(games, use_container_width=True)

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        st.header("📊 Análisis de Valor IA")
        col1, col2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (col1 if idx % 2 == 0 else col2):
                st.info(f"**{r['partido']}**\n\nPick: **{r['pick']}** | Prob: {r['probabilidad']}%")

        if parlay:
            st.markdown("---")
            st.header("🔥 Tu Ticket Profesional")
            monto = st.number_input("💰 Monto (MXN)", value=10.0, step=5.0)
            sim = engine.simulate_parlay_profit(parlay, monto)

            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:10px;">
                    <small style="color:gray;">{p['partido']}</small><br>
                    <b style="color:#00ff9d; font-size:18px;">Sí → {p['pick']}</b><br>
                    <small>Cuota: {p['cuota']} | Confianza: {'⭐' * (int(p['probabilidad']/20))}</small>
                </div>
                """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']}")
            m2.metric("Pago Total", f"${sim['pago_total']}")
            m3.metric("Ganancia", f"${sim['ganancia_neta']}")

            if st.button("💾 Registrar como Apostado"):
                st.success("¡Parlay guardado!")
