import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico

st.set_page_config(page_title="BETTING AI", layout="wide")

# --- SIDEBAR: HISTORIAL SEGURO ---
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        try:
            hist = pd.read_csv("parlay_history.csv")
            if not hist.empty:
                # Usamos .get para evitar errores si la columna no existe aún
                apostado = hist.get('monto', pd.Series([0])).sum()
                ganancia = hist.get('ganancia_neta', pd.Series([0])).sum()
                st.metric("ROI Total", f"{(ganancia/apostado*100 if apostado > 0 else 0):.1f}%")
                st.markdown("---")
                for _, r in hist.tail(5).iterrows():
                    fecha = r.get('Fecha', 'S/F')
                    neta = r.get('ganancia_neta', 0.0)
                    st.write(f"📅 {fecha} | **${neta:.2f}**")
        except:
            st.error("Error al cargar historial")
    else:
        st.info("Sin registros aún")

# --- APP PRINCIPAL ---
st.title("🤖 PARLAY MAESTRO — Filtro 85%")
archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando con Visión por Proximidad..."):
        # Llamada a tu función optimizada (la que usa bounding_box)
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación de Partidos Detectados (OCR)"):
            st.dataframe(games, use_container_width=True)

        # Usamos tu EVEngine con el umbral de élite
        engine = EVEngine(threshold=0.85)
        resultados, parlay = engine.build_parlay(games)

        st.header("🎯 Análisis de Capas (>85%)")
        
        # Grid para mostrar el análisis de cada partido detectado
        c1, c2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (c1 if idx % 2 == 0 else c2):
                if r.get('pasa_filtro', False):
                    st.success(f"✅ **{r['partido']}**\n\nPick: **{r['pick']}** | **{r['probabilidad']}%**")
                else:
                    st.warning(f"❌ **{r['partido']}**\n\nPick: **{r['pick']}** | {r['probabilidad']}% (Bajo el 85%)")

        # --- SECCIÓN DEL TICKET FINAL ---
        if parlay:
            st.markdown("---")
            st.header("🔥 Sugerencia de Parlay Élite")
            
            monto = st.number_input("💰 Inversión (MXN)", value=100.0, step=50.0)
            sim = engine.simulate_parlay_profit(parlay, monto)
            
            # Tarjetas visuales de los picks del Parlay
            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e
