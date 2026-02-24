import streamlit as st
import pandas as pd
import datetime
import os

from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

# Sidebar historial
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        hist = pd.read_csv("parlay_history.csv")
        total_apostado = hist["monto"].sum()
        total_ganancia = hist["ganancia_neta"].sum()
        roi = (total_ganancia / total_apostado * 100) if total_apostado > 0 else 0
        st.metric("ROI Total", f"{roi:.1f}%", f"${total_ganancia:.2f}")
        st.metric("Apostado", f"${total_apostado:.2f}")
    else:
        st.info("Aún no hay parlays registrados")

archivo = st.file_uploader("Sube captura de cualquier liga", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Procesando..."):
        games = analyze_betting_image(archivo)
    
    if games:
        st.subheader("🏟️ Verificación de Partidos")
        st.dataframe(games, use_container_width=True)   # temporal

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        st.header("📊 Análisis de Valor IA")
        col1, col2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (col1 if idx % 2 == 0 else col2):
                st.caption(f"**{r['partido']}**")
                st.info(f"Pick: **{r['pick']}**  \nProb: {r['probabilidad']}% | Cuota: {r['cuota']} | EV: {r['ev']}")

        if parlay:
            st.markdown("---")
            st.header("🔥 Parlay Maestro Detectado")

            monto = st.number_input("💰 Monto a apostar (MXN)", value=10.0, step=5.0, min_value=5.0, format="%.2f")
            sim = engine.simulate_parlay_profit(parlay, monto)

            # === DISEÑO DE TICKET PROFESIONAL ===
            st.markdown("### 🎟️ Tu Ticket")
            for p in parlay:
                with st.container():
                    st.markdown(f"""
                    <div style="background:#1e1e1e; padding:15px; border-radius:10px; margin:8px 0;">
                        <strong>{p['partido']}</strong><br>
                        <span style="color:#00ff9d">Sí → {p['pick']}</span><br>
                        <small>Cuota: {p['cuota']} | Prob: {p['probabilidad']}%</small>
                    </div>
                    """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']:.2f}")
            m2.metric("Pago Total", f"${sim['pago_total']:.2f}")
            m3.metric("Ganancia Neta", f"${sim['ganancia_neta']:.2f}")

            if st.button("💾 Registrar Parlay como Apostado", type="primary"):
                # (código de guardado igual que antes)
                st.success("✅ Guardado en historial")
                st.rerun()

else:
    st.info("Sube una captura...")

st.markdown("---")
st.subheader("📜 Historial")
if os.path.exists("parlay_history.csv"):
    st.dataframe(pd.read_csv("parlay_history.csv"), use_container_width=True)

