import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico, update_pending_parlays
from modules.context_search import get_team_context, analyze_context
from modules.bankroll import obtener_stake_sugerido

# Configuración de Interfaz Profesional
st.set_page_config(page_title="BETTING AI - CEREBRO DE AUDITORÍA", layout="wide")

# Inicialización de servicios
update_pending_parlays()
engine = EVEngine()

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #00ff9d; font-weight: bold; margin-bottom: 20px; }
    .card { background: #1e1e1e; padding: 20px; border-radius: 15px; border-left: 5px solid #00ff9d; margin-bottom: 15px; }
    .metric-box { text-align: center; padding: 10px; background: #262730; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🤖 CEREBRO DE AUDITORÍA ESTRATÉGICA</div>', unsafe_allow_html=True)

# --- SIDEBAR: GESTIÓN FINANCIERA ---
with st.sidebar:
    st.header("💰 Gestión de Capital")
    bankroll_total = st.number_input("Capital Total Disponible (MXN)", value=1000.0, step=100.0)
    st.markdown("---")
    st.info("Este Cerebro utiliza **Half-Kelly** para proteger tu capital contra rachas negativas.")

# --- CARGA Y PROCESAMIENTO ---
archivo = st.file_uploader("📂 Cargar Captura (PC o Móvil)", type=["jpg", "png", "jpeg"])

if archivo:
    # 1. OCR e Inteligencia Visual
    with st.spinner("🧠 Leyendo mercados y detectando equipos..."):
        matches, debug_rows = analyze_betting_image(archivo)
    
    # Debug OCR (Opcional, expandible)
    with st.expander("🔍 Verificación de Datos OCR (Debug)", expanded=False):
        for row in debug_rows:
            st.write(row)

    if matches:
        st.subheader("🏟️ Análisis de Auditoría por Partido")
        
        picks_para_parlay = []
        
        # Procesar cada partido con el "Cerebro"
        for i, game in enumerate(matches):
            with st.container():
                col_info, col_stats = st.columns([2, 1])
                
                # A. Búsqueda de Contexto Real (Google API)
                with st.spinner(f"🌐 Buscando noticias de {game['home']}..."):
                    raw_context = get_team_context(game['home'])
                    context_factors = analyze_context(raw_context)
                
                # B. Análisis Multivariable (Poisson + Auditoría)
                analisis = engine.get_advanced_analysis(game, context_factors)
                picks_para_parlay.append(analisis)
                
                # C. Interfaz de Usuario por Partido
                with col_info:
                    st.markdown(f"""
                    <div class="card">
                        <h3 style="margin:0;">{game['home']} vs {game['away']}</h3>
                        <p style="color:#00ff9d; font-size:1.2rem; margin:10px 0;">🎯 Pick Sugerido: <b>{analisis['pick']}</b></p>
                        <p style="font-size:0.9rem; color:#aaa;">{raw_context[:180]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_stats:
                    confianza = analisis['prob']
                    stake_recom = obtener_stake_sugerido(bankroll_total, confianza)
                    
                    st.markdown(f'<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Confianza IA", f"{confianza}%")
                    st.metric("Stake Sugerido", f"${stake_recom}")
                    st.markdown('</div>', unsafe_allow_html=True)

        # --- TICKET FINAL DE PARLAY ---
        st.markdown("---")
        st.subheader("🎟️ Ticket de Auditoría Consolidado")
        
        # Simulación de Ganancias
        monto_final = st.number_input("Monto final a apostar (MXN)", value=float(obtener_stake_sugerido(bankroll_total, 80)), step=10.0)
        sim = engine.simulate_parlay_profit(picks_para_parlay, monto_final)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cuota Total", f"{sim['cuota_total']}x")
        c2.metric("Pago Potencial", f"${sim['pago_total']}")
        c3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")
        
        # Cálculo de ROI Esperado
        roi = round((sim['ganancia_neta'] / monto_final) * (sum([p['prob'] for p in picks_para_parlay])/len(picks_para_parlay) / 100) * 100, 2)
        c4.metric("ROI Est. (Valor)", f"{roi}%")

        if st.button("🚀 REGISTRAR Y CERRAR AUDITORÍA", use_container_width=True):
            resumen_picks = " | ".join([p['pick'] for p in picks_para_parlay])
            registrar_parlay_automatico(sim, resumen_picks)
            st.balloons()
            st.success("¡Parlay enviado al historial de seguimiento!")

# --- HISTORIAL Y APRENDIZAJE ---
st.markdown("---")
st.subheader("📅 Historial de Desempeño")
if os.path.exists("data/parlay_history.csv"):
    df_h = pd.read_csv("data/parlay_history.csv")
    st.dataframe(df_h.tail(10), use_container_width=True)
