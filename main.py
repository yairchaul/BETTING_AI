import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico, update_pending_parlays

# Configuración Responsive
st.set_page_config(page_title="Betting AI Móvil", layout="wide")

# Estilo CSS para tarjetas tipo móvil
st.markdown("""
    <style>
    .stMetric { background: #262730; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    .bet-card { 
        background: #1e1e1e; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 6px solid #00ff9d; 
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

update_pending_parlays()

st.title("📱 Parlay Maestro")

archivo = st.file_uploader("Subir Ticket o Captura", type=["jpg", "png", "jpeg"])

if archivo:
    # Mostrar la imagen que subiste para confirmación visual
    st.image(archivo, caption="Imagen cargada", use_column_width=True)
    
    with st.spinner("Analizando mercados..."):
        games = analyze_betting_image(archivo)
    
    if games:
        st.subheader("✅ Partidos Detectados")
        # Visualización adaptada a móvil (tarjetas en lugar de tabla)
        for g in games:
            st.markdown(f"""
            <div class="bet-card">
                <small style="color:#888;">Mercado: {g.get('market','1X2')}</small><br>
                <b>{g.get('home','Equipo 1')}</b> ({g.get('home_odd','N/A')}) vs <br>
                <b>{g.get('away','Equipo 2')}</b> ({g.get('away_odd','N/A')})
            </div>
            """, unsafe_allow_html=True)

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)
        
        st.markdown("---")
        monto = st.number_input("💰 Inversión (MXN)", value=100.0, step=50.0)
        sim = engine.simulate_parlay_profit(parlay, monto)
        sim['monto'] = monto

        # Métricas principales redondeadas
        c1, c2, c3 = st.columns(3)
        c1.metric("Cuota", f"{round(sim['cuota_total'], 2)}x")
        c2.metric("Pago", f"${round(sim['pago_total'], 2)}")
        c3.metric("Neto", f"${round(sim['ganancia_neta'], 2)}")

        if st.button("🚀 REGISTRAR APUESTA", use_container_width=True):
            picks_txt = " | ".join([p['pick'] for p in parlay])
            registrar_parlay_automatico(sim, picks_txt)
            st.balloons()
            st.success("¡Parlay registrado!")

# Historial resumido para móvil
st.markdown("---")
st.subheader("🏁 Historial Reciente")
if os.path.exists("data/parlay_history.csv"):
    df = pd.read_csv("data/parlay_history.csv").tail(5)
    st.dataframe(df[['Fecha', 'Picks', 'Estado']], use_container_width=True)

