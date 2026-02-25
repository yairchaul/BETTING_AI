import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico

st.set_page_config(page_title="BETTING AI", layout="wide")

# --- SIDEBAR SEGURO ---
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        hist = pd.read_csv("parlay_history.csv")
        if not hist.empty:
            st.metric("ROI", f"{(hist['ganancia_neta'].sum()/hist['monto'].sum()*100 if hist['monto'].sum()>0 else 0):.1f}%")
            st.markdown("---")
            for _, r in hist.tail(5).iterrows():
                # Uso de .get para evitar KeyError si la columna falta
                fecha = r.get('Fecha', 'S/F')
                neta = r.get('ganancia_neta', 0)
                st.write(f"📅 {fecha} | **${neta:.2f}**")

# --- MAIN APP ---
st.title("🤖 PARLAY MAESTRO (Filtro 85%)")
archivo = st.file_uploader("Sube captura", type=["png", "jpg", "jpeg"])

if archivo:
    games = analyze_betting_image(archivo)
    if games:
        engine = EVEngine(threshold=0.85)
        resultados, parlay = engine.build_parlay(games)

        st.header("🎯 Picks Seleccionados (>85%)")
        if not resultados:
            st.warning("Ningún mercado superó el filtro del 85%.")
        
        for r in resultados:
            st.success(f"**{r['partido']}** -> {r['pick']} ({r['probabilidad']}%)")

        if parlay:
            st.markdown("---")
            monto = st.number_input("Monto", value=100.0)
            sim = engine.simulate_parlay_profit(parlay, monto)
            
            st.metric("Cuota Total", f"{sim['cuota_total']}x")
            
            if st.button("💾 REGISTRAR APUESTA"):
                sim['monto'] = monto
                registrar_parlay_automatico(sim, " | ".join([p['pick'] for p in parlay]))
                st.balloons()
                st.rerun()

