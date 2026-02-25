import streamlit as st
import pandas as pd
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.context_search import get_team_context, analyze_context
from modules.learning import LearningModule
from modules.cerebro import CerebroAuditor
from modules.bankroll import obtener_stake_sugerido

# Inicializar Módulos
learning = LearningModule()
auditor = CerebroAuditor()
engine = EVEngine()

st.title("🧠 Betting AI: Sistema de Auditoría Total")

archivo = st.file_uploader("Cargar Ticket", type=["jpg", "png", "jpeg"])

if archivo:
    matches, _ = analyze_betting_image(archivo)
    
    if matches:
        picks_finales = []
        
        for game in matches:
            # 1. Obtener Datos de 3 Fuentes
            poisson_raw = engine.get_raw_probabilities(game)
            
            with st.spinner(f"Investigando context de {game['home']}..."):
                raw_txt = get_team_context(game['home'])
                context_f = analyze_context(raw_txt)
            
            # Simulación de línea (ej. 2.5 goles) para Learning
            learning_f = learning.analizar_valor_historico(game['home'], 2.5)
            
            # 2. EL CEREBRO TOMA LA DECISIÓN
            veredicto = auditor.decidir_mejor_apuesta(poisson_raw, context_f, learning_f)
            picks_finales.append(veredicto)
            
            # 3. Mostrar Auditoría
            with st.expander(f"📋 Auditoría: {game['home']} vs {game['away']}", expanded=True):
                c1, c2 = st.columns([2,1])
                c1.write(f"### Pick: **{veredicto['pick_final']}**")
                c1.info(veredicto['nota'])
                
                # Gestión de Bankroll aplicada al veredicto del Cerebro
                capital = 1000 # O extraer de sidebar
                stake = obtener_stake_sugerido(capital, veredicto['confianza_final'])
                
                c2.metric("Confianza Final", f"{veredicto['confianza_final']}%")
                c2.metric("Stake Sugerido", f"${stake}")
                
        # Simulación de Parlay
        st.markdown("---")
        if st.button("🚀 Registrar Parlay Auditado"):
            st.success("Analizado y Guardado con éxito.")
