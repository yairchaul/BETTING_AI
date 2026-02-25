import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
# IMPORTACIÓN CORREGIDA:
from modules.tracker import registrar_parlay_automatico, update_pending_parlays

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")

# 1. Actualización automática al arrancar la app
update_pending_parlays()

st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

archivo = st.file_uploader("Sube tu captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando mercados..."):
        games = analyze_betting_image(archivo)
    
    if games:
        # Verificación de partidos ocultable
        with st.expander("🏟️ Verificación de Partidos Detectados", expanded=False):
            st.dataframe(games, use_container_width=True)

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        st.header("🔥 Simulación de Parlay Sugerido")
        monto = st.number_input("💰 Inversión (MXN)", value=100.0, step=50.0)
        
        # Cálculos de cuota multiplicada
        sim = engine.simulate_parlay_profit(parlay, monto)
        sim['monto'] = monto

        # Mostrar picks
        for p in parlay:
            st.markdown(f"""
            <div style="background:#1e1e1e; padding:12px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:8px;">
                <b style="color:#00ff9d;">{p['pick']}</b><br>
                <small>{p['partido']} | Momio: {p['cuota']}</small>
            </div>
            """, unsafe_allow_html=True)

        # Métricas principales
        c1, c2, c3 = st.columns(3)
        c1.metric("Cuota Final", f"{sim['cuota_total']}x")
        c2.metric("Pago Potencial", f"${sim['pago_total']}")
        c3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")

        if st.button("🚀 Registrar para Seguimiento Automático", use_container_width=True):
            picks_txt = " | ".join([p['pick'] for p in parlay])
            registrar_parlay_automatico(sim, picks_txt)
            st.success("Apuesta registrada. El sistema buscará el resultado automáticamente.")

# --- HISTORIAL VISUAL ---
st.markdown("---")
st.subheader("🏁 Estatus de tus Parlays")
if os.path.exists("data/parlay_history.csv"):
    df_h = pd.read_csv("data/parlay_history.csv")
    
    def style_status(val):
        color = '#2ecc71' if val == 'Ganada' else '#e74c3c' if val == 'Perdida' else '#f1c40f'
        return f'background-color: {color}; color: black; font-weight: bold'

    st.dataframe(df_h.style.applymap(style_status, subset=['Estado']), use_container_width=True)

