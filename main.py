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

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Betting AI - Valor IA", layout="wide")

st.markdown("""
    <style>
    .valor-card {
        background-color: #1a2c3d;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        border-left: 6px solid #1E88E5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .pick-header { color: #42A5F5; font-weight: bold; font-size: 1.3rem; margin-bottom: 5px; }
    .badge-alta { background-color: #2ecc71; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; }
    .badge-media { background-color: #f1c40f; color: black; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; }
    .badge-riesgo { background-color: #e74c3c; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# Instanciar Módulos
engine = EVEngine()
learning = LearningModule()
auditor = CerebroAuditor()

st.title("📊 Análisis de Valor IA")

archivo = st.file_uploader("Cargar Ticket de Apuestas", type=["jpg", "png", "jpeg"])

if archivo:
    st.image(archivo, width=280)
    matches, _ = analyze_betting_image(archivo)
    
    if matches:
        picks_auditados = []
        cols = st.columns(2)
        
        for i, game in enumerate(matches):
            # 1. Obtener Edge Matemático (Poisson Pro)
            poisson_raw = engine.get_raw_probabilities(game)
            
            # 2. Obtener Contexto Real (Google)
            with st.spinner(f"🌐 Verificando noticias: {game['home']}..."):
                raw_txt = get_team_context(game['home'])
                context_f = analyze_context(raw_txt)
            
            # 3. Obtener Historial (Learning)
            learning_f = learning.analizar_valor_historico(game['home'])
            
            # 4. Auditoría del Cerebro
            veredicto = auditor.decidir_mejor_apuesta(poisson_raw, context_f, learning_f)
            picks_auditados.append(veredicto)
            
            # 5. Renderizado Estilo "Valor IA"
            with cols[i % 2]:
                badge_class = f"badge-{veredicto['estatus'].lower()}"
                st.markdown(f"""
                <div class="valor-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span class="pick-header">{game['home']} vs {game['away']}</span>
                        <span class="{badge_class}">{veredicto['estatus']}</span>
                    </div>
                    <p style="margin: 10px 0; font-size: 1.1rem;">🎯 Pick: <b>{veredicto['pick_final']}</b></p>
                    <p style="font-size: 0.9rem; color: #BDC3C7;">
                        Confianza Final: {veredicto['confianza_final']}% | EV: {veredicto['ev_final']}<br>
                        <i>{veredicto['nota']}</i>
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # --- SECCIÓN FINANCIERA ---
        st.markdown("---")
        c_bank, c_inv = st.columns(2)
        bankroll = c_bank.number_input("Bankroll Total (MXN)", value=1000.0)
        
        # Sugerencia de inversión basada en el promedio de confianza del parlay
        conf_promedio = sum([p['confianza_final'] for p in picks_auditados]) / len(picks_auditados)
        stake_sugerido = obtener_stake_sugerido(bankroll, conf_promedio)
        
        monto_final = c_inv.number_input("Inversión Final Parlay", value=float(stake_sugerido))
        
        # Simulación del Parlay
        sim = engine.simulate_parlay_profit(picks_auditados, monto_final)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Cuota Final", f"{sim['cuota_total']}x")
        col2.metric("Pago Potencial", f"${sim['pago_total']}")
        col3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")

        if st.button("🚀 REGISTRAR EN EL TRACKER DE VALOR", use_container_width=True):
            resumen = " | ".join([p['pick_final'] for p in picks_auditados])
            registrar_parlay_automatico(sim, resumen)
            st.success("✅ Parlay guardado exitosamente en el historial.")
            st.rerun()

# --- HISTORIAL VISUAL (ESTATUS) ---
st.markdown("### 🏁 Estatus y Seguimiento de Parlays")
if os.path.exists(PATH_HISTORIAL):
    df_h = pd.read_csv(PATH_HISTORIAL)
    
    def style_estado(val):
        color = '#2ecc71' if val == 'Ganado' else '#e74c3c' if val == 'Perdido' else '#f1c40f'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_h.sort_index(ascending=False).style.applymap(style_estado, subset=['Estado']), use_container_width=True)
