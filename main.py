import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico, update_pending_parlays

st.set_page_config(page_title="BETTING AI - ANÁLISIS PRO", layout="wide")

update_pending_parlays()

st.title("🔬 Sistema de Análisis Partido a Partido")

archivo = st.file_uploader("Subir imagen de momios", type=["jpg", "png", "jpeg"])

if archivo:
    # Procesar imagen
    matches, debug_rows = analyze_betting_image(archivo)
    
    # 1. DEBUG OCR (Restaurado)
    with st.expander("🔍 Verificación de Datos OCR (Debug)", expanded=False):
        for row in debug_rows:
            st.write(row)

    if matches:
        # 2. VERIFICACIÓN DE PARTIDOS (Restaurada)
        st.subheader("🏟️ Partidos e Información Detectada")
        st.dataframe(pd.DataFrame(matches), use_container_width=True)

        # 3. ANÁLISIS INDIVIDUAL
        engine = EVEngine()
        st.subheader("🎯 Análisis de Probabilidad y Mejor Opción")
        
        col1, col2 = st.columns(2)
        parlay_picks = []

        for i, game in enumerate(matches):
            analisis = engine.get_best_ev_pick(game)
            parlay_picks.append(analisis)
            
            with (col1 if i % 2 == 0 else col2):
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #00ff9d; margin-bottom:10px;">
                    <h4 style="margin:0;">{analisis['partido']}</h4>
                    <p style="margin:5px 0;">Sugerencia IA: <b style="color:#00ff9d;">{analisis['pick']}</b></p>
                    <small>Confianza: {analisis['prob']}% | Momio Ref: {analisis['cuota']}</small>
                </div>
                """, unsafe_allow_html=True)

        # 4. CÁLCULO DE PARLAY
        st.markdown("---")
        monto = st.number_input("Inversión para el Parlay", value=100.0, step=50.0)
        sim = engine.simulate_parlay_profit(parlay_picks, monto)

        c1, c2, c3 = st.columns(3)
        c1.metric("Cuota Final", f"{sim['cuota_total']}x")
        c2.metric("Pago Total", f"${sim['pago_total']}")
        c3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")

        if st.button("🚀 REGISTRAR PARLAY PARA SEGUIMIENTO", use_container_width=True):
            picks_txt = " | ".join([p['pick'] for p in parlay_picks])
            registrar_parlay_automatico(sim, picks_txt)
            st.success("Apuesta registrada correctamente.")

# Historial al final
if os.path.exists("data/parlay_history.csv"):
    st.markdown("---")
    st.subheader("📅 Historial de Análisis")
    st.dataframe(pd.read_csv("data/parlay_history.csv").tail(5), use_container_width=True)
