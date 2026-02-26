import streamlit as st
import os
import sys

# Inyectar el path de modules para evitar ImportErrors en Streamlit Cloud
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.vision_reader import read_ticket_image
from modules.cerebro import obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="BETTING AI EV+ PRO", layout="wide")

st.title("🧠 BETTING AI — Sharp Money Detector")

uploaded = st.file_uploader("Sube los momios de Caliente", type=["png", "jpg", "jpeg"])

if uploaded:
    with st.status("Analizando últimos 5 partidos y 13 mercados...", expanded=True) as status:
        # 1. OCR
        games_data = read_ticket_image(uploaded)
        
        if not games_data:
            st.error("No se detectaron datos en la imagen.")
            st.stop()
            
        # 2. Análisis exhaustivo individual
        results = []
        for partido in games_data:
            mejor_pick = obtener_mejor_apuesta(partido)
            if mejor_pick:
                results.append({"pick": mejor_pick})
        
        status.update(label="Análisis finalizado con éxito", state="complete")

    if results:
        st.subheader("🔥 Picks con Mayor Probabilidad Detectados")
        for res in results:
            r = res["pick"]
            with st.expander(f"📍 {r.match} | {r.selection}", expanded=True):
                c1, c2 = st.columns(2)
                c1.metric("Ventaja (EV)", f"{round(r.ev * 100, 1)}%")
                c2.metric("Momio Detectado", f"{r.odd}")

        # 3. Smart Parlay y Calculadora Financiera
        st.divider()
        parlay = build_smart_parlay([res["pick"] for res in results])

        if parlay:
            st.subheader("🚀 Smart Parlay Sugerido")
            with st.container(border=True):
                st.write(f"**Combinada:** {' + '.join(parlay.matches)}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Cuota Total", f"{parlay.total_odd}x")
                col2.metric("Probabilidad", f"{round(parlay.combined_prob * 100, 1)}%")
                col3.metric("EV Acumulado", f"{round(parlay.total_ev, 2)}")

                st.divider()
                # CALCULADORA DE GANANCIAS
                monto = st.number_input("Inversión ($)", min_value=10.0, value=100.0, step=10.0)
                ganancia = monto * parlay.total_odd
                st.success(f"💰 **Ganancia Potencial: ${round(ganancia, 2)}**")
                
                if st.button("📥 Registrar Apuesta en Historial", use_container_width=True):
                    st.balloons()
                    st.toast("Apuesta registrada exitosamente.")
