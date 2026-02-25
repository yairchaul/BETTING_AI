import streamlit as st
import pandas as pd
import datetime
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

# --- SIDEBAR: HISTORIAL ROBUSTO ---
with st.sidebar:
    st.header("📊 Historial")
    file_path = "parlay_history.csv"
    if os.path.exists(file_path):
        try:
            hist = pd.read_csv(file_path)
            # Aseguramos que existan las columnas para evitar KeyError
            if not hist.empty and 'monto' in hist.columns:
                roi = (hist['ganancia_neta'].sum() / hist['monto'].sum() * 100) if hist['monto'].sum() > 0 else 0
                st.metric("ROI Total", f"{roi:.1f}%")
                st.metric("Apostado", f"${hist['monto'].sum():.2f}")
                
                st.markdown("---")
                st.subheader("📝 Últimos Registros")
                # Manejo de error para columna 'Fecha'
                col_fecha = 'Fecha' if 'Fecha' in hist.columns else hist.columns[0]
                for _, row in hist.tail(5).iterrows():
                    color = "🟢" if row['ganancia_neta'] > 0 else "⚪"
                    st.write(f"{color} **{row[col_fecha]}**")
                    st.caption(f"Neto: ${row['ganancia_neta']:.2f}")
        except Exception as e:
            st.error(f"Error al leer historial: {e}")
    else:
        st.info("Aún no hay parlays registrados")

archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando imagen..."):
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación de Partidos", expanded=False):
            st.dataframe(games, use_container_width=True)

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        st.header("📊 Análisis de Valor IA")
        c1, c2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (c1 if idx % 2 == 0 else c2):
                st.info(f"**{r['partido']}**\n\nPick: **{r['pick']}** | Prob: {r['probabilidad']}%")

        if parlay:
            st.markdown("---")
            st.header("🔥 Tu Ticket Profesional")
            monto = st.number_input("💰 Monto (MXN)", value=100.0, step=10.0)
            sim = engine.simulate_parlay_profit(parlay, monto)

            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:10px;">
                    <small style="color:gray;">{p['part
