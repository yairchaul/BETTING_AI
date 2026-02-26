import streamlit as st
import os
import sys
from datetime import datetime

# Inyectar el path de modules para evitar ImportErrors
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.vision_reader import read_ticket_image
from modules.cerebro import obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay
from modules.results_tracker import save_parlay, get_history

st.set_page_config(page_title="BETTING AI EV+ PRO", layout="wide")

st.title("🧠 BETTING AI — Sharp Money Detector")

# Pestañas para organizar la visualización
tab_analisis, tab_historial = st.tabs(["📊 Análisis de Imagen", "📜 Historial de Parlays"])

with tab_analisis:
    uploaded = st.file_uploader("Sube los momios de Caliente", type=["png", "jpg", "jpeg"])

    if uploaded:
        with st.status("Analizando últimos 5 partidos y 13 mercados...", expanded=True) as status:
            games_data = read_ticket_image(uploaded)
            
            if not games_data:
                st.error("No se detectaron datos en la imagen.")
                st.stop()
                
            results = []
            for partido in games_data:
                mejor_pick = obtener_mejor_apuesta(partido)
                if mejor_pick:
                    results.append({"pick": mejor_pick})
            
            status.update(label="Análisis finalizado con éxito", state="complete")

        if results:
            # --- BLOQUE UNIFICADO DE PARLAY (Sugerencia Principal) ---
            lista_picks = [res["pick"] for res in results]
            parlay = build_smart_parlay(lista_picks)

            if parlay:
                st.subheader("🚀 SUGERENCIA DE INVERSIÓN (PARLAY)")
                with st.container(border=True):
                    st.write("### 📝 Combinada a realizar:")
                    for m in parlay.matches:
                        st.write(f"✅ {m}")
                    
                    st.divider()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Cuota Final", f"{parlay.total_odd}x")
                    c2.metric("Probabilidad", f"{round(parlay.combined_prob * 100, 1)}%")
                    c3.metric("Ventaja Total", f"{round(parlay.total_ev, 2)}")
                    
                    monto = st.number_input("Cantidad a apostar ($)", min_value=10.0, value=100.0, step=10.0)
                    ganancia = monto * parlay.total_odd
                    st.success(f"💰 **Ganancia Potencial: ${round(ganancia, 2)}**")
                    
                    if st.button("📥 Registrar Apuesta en Historial", use_container_width=True):
                        # Guardar en results_tracker.py
                        save_parlay({
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "matches": parlay.matches,
                            "cuota": parlay.total_odd,
                            "monto": monto,
                            "ganancia_potencial": round(ganancia, 2)
                        })
                        st.balloons()
                        st.toast("Parlay guardado en el historial.")

            # --- DETALLES TÉCNICOS ---
            st.divider()
            with st.expander("🔍 Ver Desglose y Auditoría Individual"):
                for res in results:
                    r = res["pick"]
                    col_a, col_b = st.columns([2, 1])
                    col_a.write(f"📍 **{r.match}** -> {r.selection}")
                    col_b.write(f"EV: {round(r.ev * 100, 1)}% | Momio: {r.odd}")
        else:
            st.warning("No se encontraron picks con ventaja estadística (EV+).")

with tab_historial:
    st.subheader("📋 Registro de Apuestas")
    historial = get_history()
    
    if not historial:
        st.info("Aún no hay parlays registrados.")
    else:
        for entry in reversed(historial): # Mostrar más recientes primero
            with st.expander(f"📅 {entry['fecha']} | Cuota: {entry['cuota']}x"):
                st.write("**Selecciones:**")
                for m in entry['matches']:
                    st.write(f"- {m}")
                st.write(f"**Inversión:** ${entry['monto']} | **Premio:** ${entry['ganancia_potencial']}")
