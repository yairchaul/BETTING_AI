import streamlit as st
import os
from modules.vision_reader import read_ticket_image
from modules.ev_engine import analyze_matches, build_smart_parlay

st.set_page_config(page_title="BETTING AI EV+", layout="wide")

# Sidebar para estado del sistema
with st.sidebar:
    st.header("⚙️ Sistema")
    # Verificación manual simple sin funciones complejas
    if os.path.exists("modules/__init__.py"):
        st.success("Paquete modules: OK")
    else:
        st.warning("Falta modules/__init__.py")

st.title("🧠 BETTING AI — Sharp Money Detector")

uploaded = st.file_uploader("Sube imagen del ticket", type=["png", "jpg", "jpeg"])

if uploaded:
    with st.spinner("Analizando y procesando últimos 5 partidos..."):
        # 1. Ejecutar OCR
        games = read_ticket_image(uploaded)
        
        if not games:
            st.error("No se detectaron partidos en el ticket.")
        else:
            # 2. Ejecutar Motor de EV
            results = analyze_matches(games)

            if not results:
                st.warning("No se encontraron oportunidades con Valor Esperado (EV+) positivo.")
            else:
                st.subheader("🔥 Picks Sharp Detectados")
                
                for res in results:
                    r = res["pick"]
                    with st.expander(f"📍 {r.match} | Sugerido: {r.selection}", expanded=True):
                        c1, c2 = st.columns([1, 2])
                        c1.metric("EV", f"{round(r.ev * 100, 1)}%", delta=f"{r.odd} cuota")
                        c2.text("Desglose Probabilidades (Poisson + Últimos 5):")
                        c2.code(res["text"])

                # 3. Construir Parlay
                st.divider()
                lista_picks = [res["pick"] for res in results]
                parlay = build_smart_parlay(lista_picks)

                if parlay:
                    st.subheader("🚀 Smart Parlay Sugerido")
                    with st.container(border=True):
                        st.write(f"**Combinada:** {' + '.join(parlay.matches)}")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Cuota Total", f"{parlay.total_odd}x")
                        col2.metric("Probabilidad", f"{round(parlay.combined_prob * 100, 1)}%")
                        col3.metric("EV Total", f"{round(parlay.total_ev * 100, 1)}%")

