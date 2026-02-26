import streamlit as st
import pandas as pd
from datetime import datetime
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import analyze_matches

# --- CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="EV ELITE v4")
st.title("🧠 EV ELITE v4 — Sharp Money Detector")

# --- PERSISTENCIA DE DATOS (BET TRACKER) ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR: GESTIÓN DE BANCA ---
st.sidebar.header("💰 Gestión de Banca")
monto_base = st.sidebar.number_input("Inversión por Pick ($)", min_value=10, value=100)

# --- SUBIR TICKET ---
uploaded = st.file_uploader("Sube tu ticket de apuestas", type=["png", "jpg", "jpeg"])

if uploaded:
    games = analyze_betting_image(uploaded)
    if not games:
        st.error("❌ No se detectaron partidos")
        st.stop()

    st.subheader("📋 Partidos Detectados")
    st.dataframe(games)

    # --- ANÁLISIS IA ---
    results = analyze_matches(games)

    if not results:
        st.warning("⚠️ Ningún pick con EV positivo detectado en este set.")
    else:
        st.divider()
        st.subheader("🔥 Picks Sharp Detectados")
        
        total_ev = 0
        for i, r in enumerate(results):
            with st.container():
                col_info, col_action = st.columns([3, 1])
                
                with col_info:
                    st.success(
                        f"**{r.match}** | Sugerido: `{r.selection}`\n\n"
                        f"Probabilidad: **{r.probability}** | Cuota: **{r.odd}** | EV: **{r.ev}**"
                    )
                
                with col_action:
                    # Botón para registrar apuesta
                    if st.button(f"Registrar Apuesta", key=f"btn_{i}"):
                        new_bet = {
                            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Partido": r.match,
                            "Pick": r.selection,
                            "Cuota": r.odd,
                            "Monto": monto_base,
                            "EV": r.ev,
                            "Estado": "Pendiente"
                        }
                        st.session_state.history.append(new_bet)
                        st.toast(f"✅ Registrado: {r.match}")

                total_ev += r.ev

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Picks Totales", len(results))
        c2.metric("EV Promedio", round(total_ev/len(results), 3))
        c3.metric("Inversión Sugerida", f"${len(results) * monto_base}")

# --- SECCIÓN DE REGISTRO (HISTORIAL) ---
if st.session_state.history:
    st.divider()
    st.subheader("📝 Historial de Apuestas Registradas")
    df_history = pd.DataFrame(st.session_state.history)
    st.table(df_history)
    
    if st.button("Limpiar Historial"):
        st.session_state.history = []
        st.rerun()

