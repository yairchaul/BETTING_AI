import streamlit as st
import os
from modules.vision_reader import read_ticket_image
from modules.ev_engine import analyze_matches, build_smart_parlay

st.set_page_config(page_title="BETTING AI EV+", layout="wide")

with st.sidebar:
    st.header("⚙️ Sistema")
    # Verificación de estructura recuperada
    if os.path.exists("modules/__init__.py"):
        st.success("Paquete modules: OK")
    else:
        st.warning("Falta modules/__init__.py")
    
    st.divider()
    st.info("Analizando: 1X2, Doble Oportunidad, Ambos Anotan y Over/Under.")

st.title("🧠 BETTING AI — Sharp Money Detector")

uploaded = st.file_uploader("Sube imagen del ticket", type=["png", "jpg", "jpeg"])

if uploaded:
    with st.spinner("Analizando mercados y estadísticas de últimos 5 partidos..."):
        # 1. Recuperar verificación de partidos (OCR)
        games = read_ticket_image(uploaded)
        
        if not games:
            st.error("No se detectaron datos legibles.")
        else:
            # 2. Motor de decisiones basado en probabilidad máxima
            results = analyze_matches(games)

            if not results:
                st.warning("No se encontraron picks con ventaja estadística.")
            else:
                st.subheader("🔥 Picks Sharp Detectados")
                # Aquí el motor ya eligió la mejor opción de la lista que diste
                for res in results:
                    r = res["pick"]
                    with st.expander(f"📍 {r.match} | Decisión: {r.selection}", expanded=True):
                        col1, col2 = st.columns([1, 2])
                        col1.metric("EV", f"{round(r.ev * 100, 1)}%", delta=f"{r.odd} cuota")
                        col2.text("Análisis de Probabilidad:")
                        col2.code(res["text"])

                # 3. Parlay Sugerido con Calculadora de Inversión
                st.divider()
                lista_picks = [res["pick"] for res in results]
                parlay = build_smart_parlay(lista_picks)

                if parlay:
                    st.subheader("🚀 Smart Parlay Sugerido")
                    with st.container(border=True):
                        st.write(f"**Combinada:** {' + '.join(parlay.matches)}")
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Cuota Total", f"{parlay.total_odd}x")
                        c2.metric("Probabilidad", f"{round(parlay.combined_prob * 100, 1)}%")
                        c3.metric("EV Total", f"{parlay.total_ev}")

                        st.divider()
                        # Recuperada la opción de monto y ganancia
                        monto = st.number_input("Monto a invertir ($)", min_value=10.0, value=100.0, step=10.0)
                        ganancia = monto * parlay.total_odd
                        st.success(f"💰 **Ganancia Posible: ${round(ganancia, 2)}**")
                        
                        if st.button("📥 Registrar en Historial", use_container_width=True):
                            st.balloons()
                            st.toast("Guardado en historial de apuestas.")

