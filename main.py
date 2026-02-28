import streamlit as st
import os
import sys
from datetime import datetime

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
                st.error("No se detectaron partidos.")
                status.update(label="Error en OCR", state="error")
                st.stop()
                
            results = []
            for partido in games_data:
                # Rescate agresivo de nombres
                context = partido.get("context", "").strip()
                if context:
                    parts = context.split()
                    if len(parts) > 1:
                        # Primera palabra o primeras dos como local
                        partido["home"] = " ".join(parts[:2]) if len(parts) > 2 else parts[0]
                        # Última palabra como visitante si no hay
                        if "vs Visitante" in partido.get("away", ""):
                            partido["away"] = parts[-1]
                
                if not partido.get("home"):
                    partido["home"] = "Equipo Local"
                if not partido.get("away"):
                    partido["away"] = "Equipo Visitante"
                
                mejor_pick = obtener_mejor_apuesta(partido)
                if mejor_pick:
                    results.append({"pick": mejor_pick})
            
            status.update(label="Análisis completado", state="complete")

        if results:
            lista_picks = [res["pick"] for res in results if res.get("pick")]
            parlay = build_smart_parlay(lista_picks)

            if parlay:
                st.subheader("🚀 SUGERENCIA DE INVERSIÓN (PARLAY)")
                with st.container(border=True):
                    st.write("### 📝 Combinada recomendada:")
                    for m in parlay.get("matches", []):
                        st.write(f"✅ {m}")
                    
                    st.divider()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Cuota Final", f"{parlay.get('total_odd', 1.0)}x")
                    c2.metric("Probabilidad estimada", f"{round(parlay.get('combined_prob', 0) * 100, 1)}%")
                    c3.metric("Ventaja (EV)", f"{round(parlay.get('total_ev', 0), 2)}")
                    
                    monto = st.number_input("Cantidad a apostar ($)", min_value=10.0, value=100.0, step=10.0)
                    ganancia = monto * parlay.get("total_odd", 1.0)
                    st.success(f"💰 Ganancia potencial: ${round(ganancia, 2)}")
                    
                    if st.button("📥 Registrar apuesta", use_container_width=True):
                        save_parlay({
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "matches": parlay.get("matches", []),
                            "cuota": parlay.get("total_odd", 1.0),
                            "monto": monto,
                            "ganancia_potencial": round(ganancia, 2)
                        })
                        st.balloons()
                        st.toast("Registrada.")
            else:
                st.info("No hay picks con EV positivo para parlay.")

            st.divider()
            with st.expander("🔍 Picks individuales"):
                for res in results:
                    r = res["pick"]
                    st.write(f"**{r.get('match', 'Desconocido')}** → {r.get('selection', '?')} | EV: {round(r.get('ev', 0) * 100, 1)}% | Momio: {r.get('odd', '?')}")
        else:
            st.warning("Ningún pick con ventaja estadística.")

with tab_historial:
    st.subheader("📋 Historial")
    historial = get_history()
    if not historial:
        st.info("Sin apuestas aún.")
    else:
        for entry in reversed(historial):
            with st.expander(f"{entry['fecha']} | {entry['cuota']}x"):
                for m in entry.get('matches', []):
                    st.write(f"- {m}")
                st.write(f"Apostado: ${entry['monto']} | Posible: ${entry['ganancia_potencial']}")