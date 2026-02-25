import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
# Referencia corregida al nombre de tu archivo
from modules.tracker import registrar_parlay_automatico, update_pending_parlays

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")

# Actualización al iniciar
update_pending_parlays()

st.title("🤖 BETTING AI — PARLAY MAESTRO")

archivo = st.file_uploader("Sube tu captura", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando..."):
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación de Partidos", expanded=False):
            st.dataframe(games, use_container_width=True)

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        st.header("🔥 Análisis de Valor IA")
        monto = st.number_input("💰 Monto a apostar (MXN)", value=100.0, step=50.0)
        
        sim = engine.simulate_parlay_profit(parlay, monto)
        sim['monto'] = monto

        # Picks con formato limpio
        for p in parlay:
            st.markdown(f"""
            <div style="background:#1e1e1e; padding:12px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:8px;">
                <b style="color:#00ff9d;">{p['pick']}</b><br>
                <small>{p['partido']} | Momio: {p['cuota']}</small>
            </div>
            """, unsafe_allow_html=True)

        # Métricas redondeadas a 2 decimales
        c1, c2, c3 = st.columns(3)
        c1.metric("Cuota Final", f"{round(sim['cuota_total'], 2)}x")
        c2.metric("Pago Potencial", f"${round(sim['pago_total'], 2)}")
        c3.metric("Ganancia Neta", f"${round(sim['ganancia_neta'], 2)}")

        if st.button("🚀 Registrar para Seguimiento Automático", use_container_width=True):
            picks_txt = " | ".join([p['pick'] for p in parlay])
            registrar_parlay_automatico(sim, picks_txt)
            st.success("¡Registrado con éxito!")

# Historial con estilo
st.markdown("---")
st.subheader("🏁 Estatus de tus Parlays")
if os.path.exists("data/parlay_history.csv"):
    df_h = pd.read_csv("data/parlay_history.csv")
    st.dataframe(df_h, use_container_width=True)
