import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.cerebro import CerebroAuditor

st.set_page_config(page_title="Parlay Maestro AI", layout="wide")
engine = EVEngine(threshold=0.85)
auditor = CerebroAuditor()

# Estilos Responsive
st.markdown("""
    <style>
    .bet-card { background: #1a2c3d; padding: 15px; border-radius: 12px; border-left: 6px solid #00ff9d; margin-bottom: 15px; color: white; }
    .stMetric { background: #0e1117; border: 1px solid #333; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Parlay Maestro: Auditoría 85%")

archivo = st.file_uploader("Subir Captura", type=["jpg", "png", "jpeg"])

if archivo:
    st.image(archivo, width=250)
    with st.spinner("OCR & Auditoría en proceso..."):
        games = analyze_betting_image(archivo)
        
    if games:
        approved_picks = []
        for g in games:
            math_data = engine.get_probabilities(g)
            
            if math_data:
                # Aquí podrías llamar a tu módulo de contexto real
                res = auditor.auditar(math_data, "Información neutral")
                approved_picks.append(res)
                
                with st.container():
                    st.markdown(f"""
                    <div class="bet-card">
                        <b>{g['home']} vs {g['away']}</b><br>
                        🎯 Sugerencia: {res['pick_final']}<br>
                        <small>{res['nota']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption(f"🚫 {g['home']} vs {g['away']} descartado (<85%)")

        if approved_picks:
            st.divider()
            monto = st.number_input("Inversión (MXN)", value=100.0)
            
            # Cálculo de Parlay
            cuota_total = 1.0
            for p in approved_picks: cuota_total *= p['cuota']
            pago = monto * cuota_total
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Cuota", f"{round(cuota_total, 2)}x")
            c2.metric("Pago Potencial", f"${round(pago, 2)}")
            c3.metric("Confianza Media", f"{round(sum(p['confianza'] for p in approved_picks)/len(approved_picks), 1)}%")

            if st.button("🚀 REGISTRAR EN HISTORIAL", use_container_width=True):
                # Lógica para guardar en data/parlay_history.csv
                st.balloons()
                st.success("¡Parlay Guardado!")

# Historial
st.subheader("🏁 Historial Reciente")
if os.path.exists("data/parlay_history.csv"):
    df = pd.read_csv("data/parlay_history.csv").tail(5)
    st.dataframe(df, use_container_width=True)
