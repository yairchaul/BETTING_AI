import streamlit as st

from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.learning import save_result, success_rate
from modules.bankroll import kelly_stake
from modules.montecarlo import simulate_parlay

st.set_page_config(layout="wide")

st.title("🤖 BETTING AI — QUANT SYSTEM")

archivo = st.file_uploader("Sube ticket", type=["png","jpg","jpeg"])

if archivo:

    equipos = analyze_betting_image(archivo)

    st.write("Equipos:", equipos)

    if len(equipos) >= 2:

        engine = EVEngine()

        resultados, parlay = engine.build_parlay(equipos)

        st.header("📊 Picks IA")

        for r in resultados:
            st.info(f"{r.partido} → {r.pick} | {r.probabilidad}%")

        if parlay:

            st.header("🔥 Parlay Detectado")

            monto = st.number_input("Monto MXN", value=100.0)

            cuota_total = 1
            for p in parlay:
                cuota_total *= p.cuota
                st.success(f"{p.partido} → {p.pick}")

            pago = monto * cuota_total
            ganancia = pago - monto

            st.metric("Cuota Total", round(cuota_total,2))
            st.metric("Ganancia", round(ganancia,2))

            prob_real = simulate_parlay(parlay)

            st.metric("Probabilidad Real IA", f"{prob_real}%")

            winrate = success_rate()
            st.metric("Winrate IA", f"{winrate}%")

            for p in parlay:

                c1,c2 = st.columns(2)

                with c1:
                    if st.button(f"✅ Ganó {p.partido}"):
                        save_result(p,"win")

                with c2:
                    if st.button(f"❌ Perdió {p.partido}"):
                        save_result(p,"lose")

