import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico, update_pending_parlays

st.set_page_config(page_title="Betting AI", layout="wide")

# Estilo para tarjetas pequeñas y compactas
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    .bet-card { background: #1e1e1e; padding: 10px; border-radius: 8px; border-left: 4px solid #00ff9d; margin-bottom: 5px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

update_pending_parlays()

st.title("🤖 Parlay Maestro")

archivo = st.file_uploader("Sube captura", type=["jpg", "png", "jpeg"])

if archivo:
    # Imagen en miniatura (no ocupa toda la pantalla)
    st.image(archivo, width=250, caption="Captura cargada")
    
    with st.spinner("Analizando valor de mercado..."):
        games = analyze_betting_image(archivo)
    
    if games:
        engine = EVEngine()
        # Forzamos la construcción del parlay con la mejor opción de valor
        resultados, parlay = engine.build_parlay(games)

        st.subheader("🔥 Análisis de la Mejor Opción")
        
        # Contenedor de picks de valor
        for p in parlay:
            st.markdown(f"""
            <div class="bet-card">
                <b>{p['partido']}</b><br>
                <span style="color:#00ff9d;">🎯 Sugerido: {p['pick']}</span> | Cuota: {p['cuota']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        monto = st.number_input("Inversión (MXN)", value=100.0, step=50.0)
        sim = engine.simulate_parlay_profit(parlay, monto)

        # Métricas principales (Redondeadas)
        c1, c2, c3 = st.columns(3)
        c1.metric("Cuota Final", f"{round(sim['cuota_total'], 2)}x")
        c2.metric("Pago Potencial", f"${round(sim['pago_total'], 2)}")
        c3.metric("Ganancia Neta", f"${round(sim['ganancia_neta'], 2)}")

        if st.button("🚀 REGISTRAR PARA SEGUIMIENTO", use_container_width=True):
            registrar_parlay_automatico(sim, " | ".join([p['pick'] for p in parlay]))
            st.success("¡Registrado! Revisar historial abajo.")

# Historial
st.markdown("---")
if os.path.exists("data/parlay_history.csv"):
    st.subheader("🏁 Historial de Parlays")
    df = pd.read_csv("data/parlay_history.csv").tail(5)
    st.table(df[['Fecha', 'Picks', 'Monto', 'Estado']])

