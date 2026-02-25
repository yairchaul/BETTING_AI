import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.context_search import get_team_context, analyze_context
from modules.learning import LearningModule
from modules.cerebro import CerebroAuditor
from modules.bankroll import obtener_stake_sugerido

# Configuración
st.set_page_config(page_title="Betting AI Pro", layout="wide")
engine = EVEngine()
learning = LearningModule()
auditor = CerebroAuditor()

st.title("🧠 Betting AI: Sistema de Auditoría Total")

archivo = st.file_uploader("Cargar Ticket", type=["jpg", "png", "jpeg"])

if archivo:
    # Reducimos visualmente la imagen como pediste
    st.image(archivo, width=200)
    
    matches, debug_rows = analyze_betting_image(archivo)
    
    # Debug opcional
    with st.expander("🔍 Debug OCR"):
        for r in debug_rows: st.write(r)

    if matches:
        picks_finales = []
        st.subheader("📋 Auditoría de Partidos")
        
        for game in matches:
            # 1. Datos Matemáticos
            poisson_raw = engine.get_raw_probabilities(game)
            
            # 2. Datos de Contexto (Google) con tus fuentes
            with st.spinner(f"Investigando a {game['home']}..."):
                raw_txt = get_team_context(game['home'])
                context_f = analyze_context(raw_txt)
            
            # 3. Datos de Learning
            learning_f = learning.analizar_valor_historico(game['home'])
            
            # 4. EL CEREBRO DECIDE
            veredicto = auditor.decidir_mejor_apuesta(poisson_raw, context_f, learning_f)
            picks_finales.append(veredicto)
            
            # Visualización por partido
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{game['home']} vs {game['away']}**")
                    st.info(f"🎯 Sugerencia: {veredicto['pick_final']} | {veredicto['nota']}")
                with c2:
                    stake = obtener_stake_sugerido(1000, veredicto['confianza_final'])
                    st.metric("Confianza", f"{veredicto['confianza_final']}%")
                    st.metric("Stake", f"${stake}")

        # --- SECCIÓN DE PARLAY ---
        st.markdown("---")
        monto_parlay = st.number_input("Inversión Parlay (MXN)", value=100.0)
        sim = engine.simulate_parlay_profit(picks_finales, monto_parlay)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Cuota Final", f"{sim['cuota_total']}x")
        col2.metric("Pago Potencial", f"${sim['pago_total']}")
        col3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")
