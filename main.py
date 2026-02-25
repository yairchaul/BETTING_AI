import streamlit as st
import pandas as pd
import datetime
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

# --- SIDEBAR: HISTORIAL REPARADO ---
with st.sidebar:
    st.header("📊 Historial")
    file_path = "parlay_history.csv"
    if os.path.exists(file_path):
        try:
            hist = pd.read_csv(file_path)
            if not hist.empty:
                # Usamos .get para evitar el KeyError 'monto' si el archivo está corrupto
                apostado = hist.get('monto', pd.Series([0])).sum()
                ganancia = hist.get('ganancia_neta', pd.Series([0])).sum()
                st.metric("ROI Total", f"{(ganancia / apostado * 100 if apostado > 0 else 0):.1f}%")
                st.metric("Apostado", f"${apostado:.2f}")
                st.markdown("---")
                st.subheader("📝 Últimos Registros")
                for _, row in hist.tail(5).iterrows():
                    st.write(f"📅 {row.get('Fecha', 'S/F')} | **${row.get('ganancia_neta', 0):.2f}**")
        except:
            st.error("Error al cargar historial")
    else:
        st.info("Aún no hay apuestas en el historial.")

archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando imagen..."):
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación de Partidos", expanded=False):
            st.dataframe(games, use_container_width=True)

        engine = EVEngine(threshold=0.85)
        resultados, parlay = engine.build_parlay(games)

        st.header("📊 Análisis de Valor IA")
        col1, col2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (col1 if idx % 2 == 0 else col2):
                st.info(f"**{r['partido']}**\n\nPick: **{r['pick']}** | Prob: {r['probabilidad']}%")

        if parlay:
            st.markdown("---")
            st.header("🔥 Tu Ticket Profesional")
            monto = st.number_input("💰 Monto (MXN)", value=100.0)
            sim = engine.simulate_parlay_profit(parlay, monto)

            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:10px;">
                    <small style="color:gray;">{p['partido']}</small><br>
                    <b style="color:#00ff9d; font-size:18px;"> {p['pick']}</b><br>
                    <small>Cuota: {p['cuota']} | Prob: {p['probabilidad']}%</small>
                </div>
                """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']}x")
            m2.metric("Pago Total", f"${sim['pago_total']}")
            m3.metric("Ganancia", f"${sim['ganancia_neta']}")

            if st.button("💾 Registrar como Apostado"):
                from modules.tracker import registrar_parlay_automatico
                picks_txt = " | ".join([p['pick'] for p in parlay])
                sim['monto'] = monto
                registrar_parlay_automatico(sim, picks_txt)
                st.balloons()
                st.success("✅ ¡Apuesta registrada!")
                st.rerun()
