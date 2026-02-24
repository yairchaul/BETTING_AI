import streamlit as st

from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.results_tracker import save_result, load_results, update_result

st.title("🤖 BETTING AI — TEST MODE")

engine = EVEngine()

# ==========================
# UPLOAD IMAGEN
# ==========================
archivo = st.file_uploader("Sube ticket o partidos", type=["png", "jpg", "jpeg"])

if archivo:

    equipos = analyze_betting_image(archivo)

    st.success("Equipos detectados:")
    st.write(equipos)

    resultados, parlay = engine.build_parlay(equipos)

    st.subheader("📊 Análisis IA")

    for r in resultados:
        st.write(
            f"{r['partido']} | {r['pick']} | Prob: {r['probabilidad']}% | Cuota {r['cuota']}"
        )

    # ==========================
    # PARLAY
    # ==========================
    if parlay:

        st.subheader("🔥 Parlay Detectado")

        for p in parlay:
            st.write(f"{p['partido']} → {p['pick']}")

        monto = st.number_input(
            "💰 Monto a apostar",
            min_value=1.0,
            value=10.0,
            step=1.0
        )

        simulacion = engine.simulate_parlay_profit(parlay, monto)

        st.success(
            f"""
            Cuota Total: {simulacion['cuota_total']}
            Pago Total: ${simulacion['pago_total']}
            Ganancia Neta: ${simulacion['ganancia_neta']}
            """
        )

        if st.button("💾 Guardar Parlay para Testing"):
            save_result(
                {"teams": [p["partido"] for p in parlay]},
                "PARLAY"
            )
            st.success("Parlay guardado.")

# ==========================
# TRACKING PANEL
# ==========================
st.divider()
st.subheader("📈 Performance Tracker")

results = load_results()

for i, bet in enumerate(results):

    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

    col1.write(bet["teams"])
    col2.write(bet["prediction"])
    col3.write(bet["result"])

    outcome = col4.selectbox(
        "Resultado",
        ["PENDING", "WIN", "LOSS"],
        index=["PENDING", "WIN", "LOSS"].index(bet["result"]),
        key=i
    )

    if outcome != bet["result"]:
        update_result(i, outcome)

st.text("DEBUG OCR:")
st.text(equipos)

