import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")

# --- SIDEBAR: HISTORIAL SIN ERRORES ---
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        try:
            hist = pd.read_csv("parlay_history.csv")
            if not hist.empty:
                apostado = hist.get('monto', pd.Series([0])).sum()
                ganancia = hist.get('ganancia_neta', pd.Series([0])).sum()
                st.metric("ROI Total", f"{(ganancia/apostado*100 if apostado>0 else 0):.1f}%")
                st.markdown("---")
                for _, r in hist.tail(5).iterrows():
                    st.write(f"📅 {r.get('Fecha','S/F')} | **${r.get('ganancia_neta',0):.1f}**")
        except: 
            st.error("Error al leer historial")
    else: 
        st.info("Sin registros aún")

# --- APP PRINCIPAL ---
st.title("🤖 PARLAY MAESTRO — Filtro 85%")
archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando datos de imagen..."):
        # 1. Llamada al motor de visión
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación de Partidos Detectados"):
            st.dataframe(games)

        # 2. Llamada al motor de optimización (85%)
        engine = EVEngine(threshold=0.85)
        resultados, parlay = engine.build_parlay(games)

        st.header("📊 Análisis de Capas (Probabilidad Real)")
        
        # Mostramos todos los análisis para saber qué pasó con cada partido
        c1, c2 = st.columns(2)

