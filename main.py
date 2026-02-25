import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.context_search import get_team_context, analyze_context
from modules.learning import LearningModule
from modules.cerebro import CerebroAuditor
from modules.bankroll import obtener_stake_sugerido

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Betting AI Pro - Auditoría 85%", layout="wide")

# Instanciamos el nuevo motor con tu umbral inamovible
engine = EVEngine(threshold=0.85)
learning = LearningModule()
auditor = CerebroAuditor()

# Estilo para las tarjetas azules que te gustan
st.markdown("""
    <style>
    .card-audit {
        background-color: #1a2c3d;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2ecc71;
        margin-bottom: 10px;
    }
    .descartado {
        color: #888;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Betting AI: Sistema de Auditoría Total (Filtro 85%)")

archivo = st.file_uploader("Cargar Ticket de Apuestas", type=["jpg", "png", "jpeg"])

if archivo:
    # Miniatura de la imagen cargada
    st.image(archivo, width=200)
    
    # Motor de Visión Real (Gemini)
    matches, debug_rows = analyze_betting_image(archivo)
    
    with st.expander("🔍 Debug OCR & Data"):
        if debug_rows:
            for r in debug_rows: st.write(r)
        else:
            st.write("Datos estructurados correctamente.")

    if matches:
        picks_finales = []
        st.subheader("📋 Proceso de Auditoría en Cascada")
        
        for game in matches:
            # 1. CAPA MATEMÁTICA (El nuevo EVEngine con matriz 10x10)
            poisson_res = engine.get_raw_probabilities(game)
            
            # Solo auditamos a fondo si pasa el filtro inicial del motor
            if poisson_res['status'] == "APROBADO":
                with st.container():
                    st.markdown(f'<div class="card-audit">', unsafe_allow_html=True)
                    c1, c2
