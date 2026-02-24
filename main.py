import streamlit as st
from modules.results_tracker import save_result, load_results, update_result
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine


# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Parlay Maestro IA",
    layout="wide"
)

st.title("🎯 Parlay Maestro IA — EDGE ENGINE")


# ======================
# UPLOADER
# ======================
archivo = st.file_uploader(
    "Sube captura de apuestas",
    type=["png", "jpg", "jpeg"]
)


if archivo:

    st.image(archivo, width=400)

    if st.button("🚀 INICIAR ANÁLISIS"):

        with st.spinner("Analizando mercados..."):

            equipos = analyze_betting_image(archivo)

            if len(equipos) < 2:
                st.error("No se detectaron suficientes equipos.")
                st.stop()

            engine = EVEngine()

            resultados, parlay = engine.build_parlay(equipos)

        # ======================
        # RESULTADOS
        # ======================
        st.header("📊 Resultados del Análisis")

        for r in resultados:

            prob = r["probabilidad"]

            if prob >= 80:
                color = "#28a745"
                emoji = "🔥"
            elif prob >= 65:
                color = "#ffc107"
                emoji = "⚖️"
            else:
                color = "#dc3545"
                emoji = "⚠️"

            st.markdown(
                f"""
                <div style="border-left:6px solid {color};
                            padding:15px;
                            background:#1e1e1e;
                            margin-bottom:10px;
                            border-radius:8px;">

                {emoji} <b>{r['partido']}</b><br>
                Pick: <span style="color:{color}">{r['pick']}</span><br>
                Confianza: {prob}%

                </div>
                """,
                unsafe_allow_html=True
            )

        # ======================
        # PARLAY
        # ======================
        if parlay:
            st.success(f"✅ Parlay recomendado con {len(parlay)} selecciones")

