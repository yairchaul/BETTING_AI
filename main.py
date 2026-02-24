import streamlit as st
import pandas as pd
import datetime
import os

from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

# --- Sidebar con historial rápido ---
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        hist = pd.read_csv("parlay_history.csv")
        total_apostado = hist["monto"].sum()
        total_ganancia = hist["ganancia_neta"].sum()
        roi = (total_ganancia / total_apostado * 100) if total_apostado > 0 else 0
        st.metric("ROI Total", f"{roi:.1f}%", f"${total_ganancia:.2f}")
        st.metric("Apostado", f"${total_apostado:.2f}")
    else:
        st.info("Aún no hay parlays registrados")

archivo = st.file_uploader("Sube captura de cualquier liga (Caliente.mx)",
                          type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("🔍 Detectando partidos con IA visual..."):
        games = analyze_betting_image(archivo)
   
    if games:
        st.subheader("🏟️ Verificación de Partidos")
        check_df = []
        for i, g in enumerate(games, 1):
            check_df.append({
                "Partido": i,
                "Local": g["home"],
                "Odd Local": g["home_odd"],
                "Empate": g["draw_odd"],
                "Visitante": g["away"],
                "Odd Visitante": g["away_odd"]
            })
        st.dataframe(check_df, use_container_width=True)

        # === ANÁLISIS EV + PARLAY ===
        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        st.header("📊 Análisis de Valor IA")
        col1, col2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (col1 if idx % 2 == 0 else col2):
                st.info(f"**{r['partido']}**\n"
                        f"Pick: {r['pick']} | Prob: {r['probabilidad']}% | Cuota: {r['cuota']} | EV: {r['ev']}\n"
                        f"**Razón:** {r.get('razon', 'Modelo universal Poisson')}\n"
                        f"**Goles esperados totales:** {r.get('expected_total', '?')}")

        if parlay:
            st.markdown("---")
            st.header("🔥 Parlay Maestro Detectado")

            monto = st.number_input("💰 Monto a apostar (MXN)", value=100.0, step=10.0, min_value=10.0)

            sim = engine.simulate_parlay_profit(parlay, monto)

            for p in parlay:
                st.write(f"✅ {p['partido']} → {p['pick']} (Cuota {p['cuota']})")

            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']}")
            m2.metric("Pago Total", f"${sim['pago_total']}")
            m3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")

            # === BOTÓN PARA REGISTRAR EN HISTÓRICO ===
            if st.button("💾 Registrar Parlay como Apostado", type="primary"):
                history_file = "parlay_history.csv"
                new_row = {
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "monto": monto,
                    "cuota_total": sim['cuota_total'],
                    "pago_total": sim['pago_total'],
                    "ganancia_neta": sim['ganancia_neta'],
                    "num_legs": len(parlay),
                    "picks": " | ".join([f"{p['partido']} → {p['pick']}" for p in parlay]),
                    "status": "Pendiente"
                }

                if os.path.exists(history_file):
                    df = pd.read_csv(history_file)
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    df = pd.DataFrame([new_row])
                df.to_csv(history_file, index=False)
                st.success("✅ Parlay guardado en historial!")
                st.rerun()

    else:
        st.error("No se detectaron partidos.")
else:
    st.info("Sube una captura para empezar...")

# === HISTÓRICO COMPLETO ===
st.markdown("---")
st.subheader("📜 Historial Completo de Parlays")
if os.path.exists("parlay_history.csv"):
    hist = pd.read_csv("parlay_history.csv")
    st.dataframe(hist, use_container_width=True)
else:
    st.info("Aún no hay registros. Apuesta y regístralos para ver el seguimiento.")
