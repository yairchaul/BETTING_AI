import streamlit as st
import os
import sys
from datetime import datetime

# Inyectar path de modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.vision_reader import read_ticket_image
from modules.cerebro import obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay
from modules.results_tracker import save_parlay, get_history

st.set_page_config(page_title="BETTING AI EV+ PRO", layout="wide")

st.title("🧠 BETTING AI — Sharp Money Detector")

tab_analisis, tab_historial = st.tabs(["📊 Análisis de Imagen", "📜 Historial de Parlays"])

with tab_analisis:
    uploaded = st.file_uploader("Sube los momios de Caliente", type=["png", "jpg", "jpeg"])

    if uploaded:
        with st.status("Analizando momios...", expanded=True) as status:
            games_data = read_ticket_image(uploaded)
            
            if not games_data:
                st.error("No se detectaron partidos en la imagen.")
                status.update(label="Error en OCR", state="error")
                st.stop()
                
            results = []
            for partido in games_data:
                # Rescatar nombres si están vacíos o genéricos
                if not partido.get("home") or partido["home"] in ["Local", "Local Desconocido"]:
                    context = partido.get("context", "")
                    words = context.split()
                    if words and len(words) > 1:
                        partido["home"] = " ".join(words[:-1])  # todo menos última palabra (quizá visitante)
                    else:
                        partido["home"] = "Equipo Local"

                if not partido.get("away") or partido["away"] in ["Visitante", "Desconocido"]:
                    partido["away"] = partido.get("context", "").split()[-1] or "Equipo Visitante"
                
                mejor_pick = obtener_mejor_apuesta(partido)
                if mejor_pick:
                    results.append({"pick": mejor_pick})
            
            status.update(label="Análisis completado", state="complete")

        if results:
            lista_picks = [res["pick"] for res in results]
            parlay = build_smart_parlay(lista_picks)

            if parlay:
                st.subheader("🚀 SUGERENCIA DE INVERSIÓN (PARLAY)")
                with st.container(border=True):
                    st.write("### 📝 Combinada recomendada:")
                    for m in parlay["matches"]:
                        st.write(f"✅ {m}")
                    
                    st.divider()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Cuota Final", f"{parlay['total_odd']}x")
                    c2.metric("Probabilidad estimada", f"{round(parlay['combined_prob'] * 100, 1)}%")
                    c3.metric("Ventaja (EV)", f"{round(parlay['total_ev'], 2)}")
                    
                    monto = st.number_input("Cantidad a apostar ($)", min_value=10.0, value=100.0, step=10.0)
                    ganancia = monto * parlay["total_odd"]
                    st.success(f"💰 Ganancia potencial: ${round(ganancia, 2)}")
                    
                    if st.button("📥 Registrar esta apuesta", use_container_width=True):
                        save_parlay({
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "matches": parlay["matches"],
                            "cuota": parlay["total_odd"],
                            "monto": monto,
                            "ganancia_potencial": round(ganancia, 2)
                        })
                        st.balloons()
                        st.toast("Apuesta registrada.")
            else:
                st.info("No hay picks con EV positivo suficiente para armar parlay.")

            st.divider()
            with st.expander("🔍 Desglose individual de picks", expanded=False):
                for res in results:
                    r = res["pick"]
                    col_a, col_b = st.columns([3, 1])
                    col_a.write(f"**{r['match']}** → {r['selection']}")
                    col_b.write(f"EV: {round(r['ev'] * 100, 1)}% | Momio: {r['odd']}")
        else:
            st.warning("No se encontraron picks con ventaja estadística (EV+). Prueba otra imagen o ajusta el umbral.")

with tab_historial:
    st.subheader("📋 Historial de Apuestas")
    historial = get_history()
    
    if not historial:
        st.info("Aún no hay apuestas registradas.")
    else:
        for entry in reversed(historial):
            with st.expander(f"📅 {entry['fecha']} | Cuota: {entry['cuota']}x"):
                st.write("**Selecciones:**")
                for m in entry['matches']:
                    st.write(f"- {m}")
                st.write(f"**Apostado:** ${entry['monto']} | **Posible ganancia:** ${entry['ganancia_potencial']}")