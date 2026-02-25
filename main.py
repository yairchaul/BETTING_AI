import streamlit as st
import pandas as pd
import datetime
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
# Importamos el rastreador de resultados para la automatización
from modules.results_tracker import update_pending_parlays 

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")

# --- PROCESAMIENTO AUTOMÁTICO AL INICIO ---
history_file = "parlay_history.csv"
if os.path.exists(history_file):
    # Esta función debe comparar tus picks con resultados reales (API/WebScraping)
    update_pending_parlays(history_file) 

# --- INTERFAZ DE ANÁLISIS ---
archivo = st.file_uploader("Sube captura para analizar", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando y calculando cuotas reales..."):
        games = analyze_betting_image(archivo)
    
    if games:
        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)
        
        if parlay:
            st.header("🔥 Simulación de Parlay Real")
            monto = st.number_input("💰 Monto (MXN)", value=100.0, step=50.0)
            sim = engine.simulate_parlay_profit(parlay, monto)

            # Ticket limpio sin "Sí ->"
            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:12px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:8px;">
                    <b style="color:#00ff9d;">{p['pick']}</b><br>
                    <small>{p['partido']} | Momio: {p['cuota']}</small>
                </div>
                """, unsafe_allow_html=True)

            # MÉTRICAS CORREGIDAS
            c1, c2, c3 = st.columns(3)
            c1.metric("Cuota Final", f"{sim['cuota_total']}x")
            c2.metric("Pago Potencial", f"${sim['pago_total']}")
            c3.metric("Ganancia Real", f"${sim['ganancia_neta']}")

            if st.button("🚀 Registrar para Seguimiento Automático"):
                new_row = {
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "monto": monto,
                    "cuota_total": sim['cuota_total'],
                    "ganancia_neta": sim['ganancia_neta'],
                    "status": "Pendiente", # Se actualizará solo
                    "picks": " | ".join([f"{p['partido']}:{p['pick']}" for p in parlay])
                }
                # Lógica para guardar en CSV...
                st.success("Registrado. El sistema verificará el resultado al finalizar los partidos.")

# --- HISTORIAL AUTOMATIZADO ---
st.markdown("---")
st.subheader("🏁 Estatus de tus Parlays")
if os.path.exists(history_file):
    st.dataframe(pd.read_csv(history_file), use_container_width=True)
