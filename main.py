import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")

st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

archivo = st.file_uploader(
    "Sube tu captura de Caliente.mx / Liga MX",
    type=["png", "jpg", "jpeg"]
)

if archivo:

    with st.spinner("🧠 Vision IA reconstruyendo tabla de apuestas..."):
        equipos = analyze_betting_image(archivo)

    # DEBUG CRUDO
    st.subheader("🧪 Debug OCR")
    st.write(equipos)

    if equipos:

        st.subheader("🏟️ Verificación de Partidos")

        check_data = []

        for i in range(0, len(equipos), 2):

            if i + 1 < len(equipos):
                check_data.append({
                    "Partido": (i // 2) + 1,
                    "Local": equipos[i],
                    "Visitante": equipos[i + 1]
                })

        st.table(check_data)

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(equipos)

        st.header("📊 Análisis de Valor IA")

        col1, col2 = st.columns(2)

        for idx, r in enumerate(resultados):

            target = col1 if idx % 2 == 0 else col2

            with target:
                st.info(
                    f"**{r['partido']}**\n\n"
                    f"Pick: {r['pick']} | "
                    f"Prob: {r['probabilidad']}% | "
                    f"Cuota: {r['cuota']}"
                )

        if parlay:

            st.markdown("---")
            st.header("🔥 Parlay Maestro Detectado")

            monto = st.number_input(
                "💰 Monto a apostar",
                value=100.0,
                step=10.0
            )

            sim = engine.simulate_parlay_profit(parlay, monto)

            for p in parlay:
                st.write(f"✅ {p['partido']} → {p['pick']}")

            m1, m2, m3 = st.columns(3)

            m1.metric("Cuota Total", sim["cuota_total"])
            m2.metric("Pago Total", f"${sim['pago_total']}")
            m3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")

    else:
        st.error("No se detectaron partidos válidos.")

else:
    st.info("Esperando captura para iniciar análisis...")
