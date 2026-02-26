import os

def check_structure():
    files = [
        "modules/__init__.py",
        "modules/ev_engine.py",
        "modules/team_profiles.py",
        "modules/schemas.py"
    ]
    st.sidebar.subheader("🔍 Status de Archivos")
    for f in files:
        if os.path.exists(f):
            st.sidebar.success(f"✅ {f}")
        else:
            st.sidebar.error(f"❌ Falta: {f}")

check_structure()
import streamlit as st
from modules.vision_reader import read_ticket_image
from modules.ev_engine import analyze_matches, build_smart_parlay

st.set_page_config(page_title="BETTING AI EV+", layout="wide")
st.title("🧠 BETTING AI — Sharp Money Detector")

uploaded = st.file_uploader("Sube imagen del ticket", type=["png", "jpg", "jpeg"])

if uploaded:
    with st.spinner("Procesando imagen..."):
        # 1. OCR
        games = read_ticket_image(uploaded)
        
        if not games:
            st.error("No se detectaron partidos.")
        else:
            # 2. Motor EV
            results = analyze_matches(games)

            if not results:
                st.warning("⚠️ No se encontraron oportunidades con Valor Esperado (EV+) positivo en este ticket.")
            else:
                st.subheader("🔥 Picks Sharp Detectados")
                
                # Renderizado de Picks Individuales
                for res in results:
                    r = res["pick"]
                    with st.expander(f"📍 {r.match} | {r.selection}", expanded=True):
                        c1, c2 = st.columns([1, 2])
                        c1.metric("EV", f"{round(r.ev * 100, 1)}%", delta=f"{r.odd} cuota")
                        c1.write(f"Prob: {int(r.probability*100)}%")
                        c2.text("Análisis completo:")
                        c2.code(res["text"])

                # 3. Parlay
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

