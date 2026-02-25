import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.results_tracker import registrar_parlay_automatico, update_pending_parlays

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")

# 1. Actualización automática de resultados al iniciar
history_path = "data/parlay_history.csv"
update_pending_parlays(history_path)

st.title("🤖 BETTING AI — PARLAY MAESTRO")

# --- CARGA DE CAPTURA ---
archivo = st.file_uploader("Sube tu captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Procesando imagen y mercados..."):
        games = analyze_betting_image(archivo)
    
    if games:
        # SECCIÓN OCULTABLE: Verificación de Partidos
        with st.expander("🏟️ Verificación de Partidos (Click para ver/ocultar)", expanded=False):
            st.dataframe(games, use_container_width=True)

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        st.header("🔥 Simulación de Parlay Real")
        monto = st.number_input("💰 Inversión (MXN)", value=100.0, step=50.0)
        
        # Cálculos de cuota total multiplicada
        sim = engine.simulate_parlay_profit(parlay, monto)
        sim['monto'] = monto

        # Mostrar picks en formato limpio
        for p in parlay:
            st.markdown(f"""
            <div style="background:#1e1e1e; padding:12px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:8px;">
                <b style="color:#00ff9d;">{p['pick']}</b><br>
                <small>{p['partido']} | Cuota: {p['cuota']}</small>
            </div>
            """, unsafe_allow_html=True)

        # Métricas de ganancias reales
        c1, c2, c3 = st.columns(3)
        c1.metric("Cuota Final", f"{sim['cuota_total']}x")
        c2.metric("Pago Potencial", f"${sim['pago_total']}")
        c3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")

        if st.button("🚀 Registrar para Seguimiento Automático", use_container_width=True):
            picks_txt = " | ".join([p['pick'] for p in parlay])
            registrar_parlay_automatico(sim, picks_txt)
            st.success("Registrado. El sistema verificará los resultados automáticamente.")

# --- HISTORIAL AUTOMATIZADO ---
st.markdown("---")
st.subheader("🏁 Historial y Resultados")
if os.path.exists(history_path):
    df_h = pd.read_csv(history_path)
    
    def style_status(val):
        color = '#2ecc71' if val == 'Ganada' else '#e74c3c' if val == 'Perdida' else '#f1c40f'
        return f'background-color: {color}; color: black; font-weight: bold'

    st.dataframe(df_h.style.applymap(style_status, subset=['Estado']), use_container_width=True)
