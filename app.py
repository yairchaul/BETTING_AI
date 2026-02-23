import streamlit as st
import os
import sys

sys.path.append(os.path.abspath("modules"))

from modules.connector import get_live_data
from modules.vision_reader import analyze_betting_image
from modules.tracker import log_pick
from modules.ev_engine import calcular_ev
from modules.montecarlo import simular_total
from modules.bankroll import obtener_stake_sugerido
from modules.ev_scanner import scan_ev_opportunities

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="Ticket Pro AI",
    layout="wide"
)

st.title("🔥 Ticket Pro — NBA AI Terminal")

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.header("💰 Bankroll Control")

    bankroll = st.number_input(
        "Bankroll actual",
        value=1000.0
    )

    st.metric("Stake base (10%)", f"${bankroll*0.1:.2f}")

    auto_mode = st.toggle("🤖 Auto Picks")

# ---------------- TABS ----------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📡 Live Markets",
    "📸 Vision Scanner",
    "🎯 Auto Picks",
    "💰 Tracking",
    "🧠 Mejor Parlay"
])

# =====================================================
# 📡 LIVE MARKETS
# =====================================================

with tab1:

    st.subheader("Mercados en vivo")

    with st.spinner("Conectando sportsbook..."):
        juegos = get_live_data()

    if not juegos:
        st.warning("No se detectaron juegos")
    else:

        for g in juegos:

            prob = simular_total(220)
            ev = calcular_ev(prob)

            if ev > 0.03:

                stake = obtener_stake_sugerido(bankroll, 80)

                st.success(
                    f"{g['away']} @ {g['home']} | EV {ev*100:.2f}% | Stake ${stake:.2f}"
                )

                if auto_mode:
                    log_pick(g, prob)

# =====================================================
# 📸 VISION SCANNER
# =====================================================

with tab2:

    st.subheader("Subir Screenshot Caliente")

    uploaded = st.file_uploader(
        "Sube imagen",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded:

        st.image(uploaded)

        with st.spinner("Gemini Vision leyendo líneas..."):

            games = analyze_betting_image(uploaded)

        if games:

            st.success(f"{len(games)} juegos detectados")

            for g in games:
                st.json(g)

# =====================================================
# 🎯 AUTO PICKS ENGINE
# =====================================================

with tab3:

    st.subheader("Ranking Diario de Edges")

    if st.button("Generar Picks"):

        juegos = get_live_data()

        edges = []

        for g in juegos:

            prob = simular_total(220)
            ev = calcular_ev(prob)

            edges.append({
                "game": f"{g['away']} @ {g['home']}",
                "ev": ev
            })

        edges = sorted(edges, key=lambda x: x["ev"], reverse=True)

        for e in edges[:5]:
            st.write(f"🔥 {e['game']} | Edge {e['ev']*100:.2f}%")

# =====================================================
# 💰 TRACKING
# =====================================================

with tab4:

    st.subheader("Histórico de Apuestas")

    if os.path.exists("data/picks.csv"):
        st.dataframe(
            st.session_state.get("tracker_df")
        )
    else:
        st.info("Aún no hay picks registrados")

# =====================================================
# 🧠 MEJOR PARLAY
# =====================================================

with tab5:

    st.subheader("Mejor Parlay IA")

    st.info("Próximo módulo: combinación automática de edges")
    # Fragmento para insertar en app.py después de analizar la imagen
if st.button("🔥 Analizar con IA"):
    with st.spinner("IA leyendo mercados..."):
        datos = analyze_betting_image(archivo)
        
        if datos and "juegos" in datos:
            for juego in datos["juegos"]:
                # 1. Calculamos la ventaja (ejemplo 5% de ventaja)
                ev_detectado = 0.05 
                stake_dinamico = bankroll * 0.02 # Arriesgamos 2% del bankroll
                
                # 2. Guardamos automáticamente en la base de datos
                from modules.tracker import guardar_pick_automatico
                guardar_pick_automatico(juego, ev_detectado, stake_dinamico)
                
                st.success(f"Apuesta registrada: {juego['away']} @ {juego['home']}")
