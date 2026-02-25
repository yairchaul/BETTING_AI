import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.context_search import get_team_context, analyze_context
from modules.learning import LearningModule
from modules.cerebro import CerebroAuditor
from modules.tracker import registrar_parlay_automatico, PATH_HISTORIAL
from modules.bankroll import obtener_stake_sugerido

# Estilos e Interfaz
st.set_page_config(page_title="Betting AI Pro", layout="wide")
st.markdown("""
    <style>
    .valor-card {
        background-color: #1a2c3d;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #1E88E5;
    }
    .pick-text { color: #42A5F5; font-weight: bold; font-size: 1.2rem; }
    .estado-pendiente { background-color: #ffd700; color: black; padding: 2px 8px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# Iniciar Módulos
engine = EVEngine()
learning = LearningModule()
auditor = CerebroAuditor()

st.title("📊 Análisis de Valor IA")

archivo = st.file_uploader("Cargar Ticket", type=["jpg", "png", "jpeg"])

if archivo:
    matches, _ = analyze_betting_image(archivo)
    
    if matches:
        picks_finales = []
        cols = st.columns(2)
        
        for i, game in enumerate(matches):
            poisson_raw = engine.get_raw_probabilities(game)
            context_f = analyze_context(get_team_context(game['home']))
            learning_f = learning.analizar_valor_historico(game['home'])
            veredicto = auditor.decidir_mejor_apuesta(poisson_raw, context_f, learning_f)
            
            picks_finales.append(veredicto)
            
            with cols[i % 2]:
                st.markdown(f"""
                <div class="valor-card">
                    <h3>{game['home']} vs {game['away']}</h3>
                    <p class="pick-text">🎯 {veredicto['pick_final']}</p>
                    <p>Confianza: {veredicto['confianza_final']}% | EV: {veredicto['ev_final']}</p>
                    <small>{veredicto['nota']}</small>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        monto_input = st.number_input("Inversión (MXN)", value=100.0)
        sim = engine.simulate_parlay_profit(picks_finales, monto_input)
        sim['monto_invertido'] = monto_input # Aseguramos compatibilidad con tracker.py

        if st.button("🚀 REGISTRAR PARA SEGUIMIENTO AUTOMÁTICO"):
            resumen = " | ".join([p['pick_final'] for p in picks_finales])
            registrar_parlay_automatico(sim, resumen)
            st.success("✅ Parlay guardado y tracker activo.")
            st.rerun()

# --- SECCIÓN DE HISTORIAL VISUAL ---
st.markdown("### 🏁 Estatus de tus Parlays")
if os.path.exists(PATH_HISTORIAL):
    df_h = pd.read_csv(PATH_HISTORIAL)
    
    # Aplicar colores a los estados
    def color_estado(val):
        color = '#2ecc71' if val == 'Ganado' else '#e74c3c' if val == 'Perdido' else '#f1c40f'
        return f'background-color: {color}; color: white; font-weight: bold'

    st.dataframe(df_h.style.applymap(color_estado, subset=['Estado']), use_container_width=True)
