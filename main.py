# main.py - Versión debug mínima
import streamlit as st

try:
    from modules.bankroll import calcular_stake
    st.success("Import de bankroll OK!")
except ImportError as e:
    st.error(f"Error importando bankroll: {e}")

st.title("Ticket Pro Debug")
st.write("Si ves esto y el import OK, el problema está resuelto.")                               
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Agrega raíz al path

from modules.bankroll import calcular_stake# main.py - Versión Streamlit de Ticket Pro
import streamlit as st
import pandas as pd

# Imports limpios (sin duplicados)
from modules.autopicks import generar_picks_auto
from modules.bankroll import calcular_stake
from modules.telegram_bot import enviar_pick
from modules.connector import get_live_data  # Función real en tu connector.py
from modules.montecarlo import simular_total
from modules.ev_engine import calcular_ev
from modules.injuries import verificar_lesiones
from modules.ranking import ranking_edges
from modules.tracker import guardar_pick, calcular_roi

st.set_page_config(page_title="Ticket Pro - NBA AI", layout="wide")
st.markdown("""
    <style>
        body {background-color: #121212; color: #ffffff;}
        .stApp {background-color: #121212;}
        .sidebar .sidebar-content {background-color: #0e1117;}
        .high {border-left: 5px solid #00ff00; padding-left: 10px;}
        .medium {border-left: 5px solid #ffff00; padding-left: 10px;}
        .low {border-left: 5px solid #ff0000; padding-left: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🔥 Ticket Pro - NBA AI +EV v10.0")

# Sidebar: Bankroll y métricas
with st.sidebar:
    st.header("Bankroll")
    bankroll = st.number_input("💰 Bankroll actual (MXN)", min_value=0.0, value=10000.0, step=100.0)
    st.metric("Inversión Sugerida (10%)", f"${bankroll * 0.1:,.2f}")
    st.metric("ROI Objetivo", "550%")
    if st.button("Actualizar ROI"):
        roi = calcular_roi()
        st.success(f"ROI actual: {roi:.2f}%")

# Obtener datos vivos
with st.spinner("Extrayendo mercados de Caliente.mx..."):
    juegos = get_live_data()  # Usa la función real de connector.py

if not juegos:
    st.warning("No hay juegos o mercados disponibles hoy. Revisa conexión o Caliente.mx.")
else:
    st.success(f"Encontrados {len(juegos)} eventos/juegos.")

    picks = []
    for g in juegos:
        # Asume estructura de g (ajusta según lo que devuelva get_live_data)
        # Ejemplo: g = {'away': '...', 'home': '...', 'line': 229.5, ...}
        try:
            media_modelo = g.get("line", 0) + 4  # Tu ajuste
            prob = simular_total(media_modelo)
            ev = calcular_ev(prob)

            if ev <= 0:
                continue

            if ev > 0.08:
                confianza = "🔥 EXCELENTE"
                css_class = "high"
            elif ev > 0.04:
                confianza = "⚡ BUENA"
                css_class = "medium"
            else:
                confianza = "➖ BAJA"
                css_class = "low"

            stake = calcular_stake(bankroll, confianza)
            lesiones = verificar_lesiones(g.get("home", "Unknown"))

            juego_txt = f"{g.get('away', '?')} @ {g.get('home', '?')}"

            # Tarjeta visual
            with st.container():
                st.markdown(f"""
                    <div class="{css_class}">
                        <strong>{juego_txt}</strong><br>
                        Prob Over: {prob*100:.1f}%  
                        EV: {ev*100:.2f}%  
                        Confianza: {confianza}<br>
                        Stake sugerido: ${stake:.2f} MXN  
                        Lesiones: {lesiones}
                    </div>
                """, unsafe_allow_html=True)

            guardar_pick(juego_txt, stake, ev)
            picks.append({"game": juego_txt, "ev": ev})

            # Enviar a Telegram si es buena/excelente
            if ev > 0.04:
                texto = f"""
🔥 AUTO PICK
Juego: {juego_txt}
EV: {ev*100:.2f}%
Stake: ${stake:.2f}
                """
                try:
                    enviar_pick(texto)
                    st.info("Pick enviado a Telegram")
                except Exception as e:
                    st.error(f"Error enviando a Telegram: {e}")

        except Exception as e:
            st.error(f"Error procesando juego {g}: {e}")
            continue

    # Ranking y ROI final
    if picks:
        ranking_edges(picks)
        roi = calcular_roi()
        st.subheader("Resumen")
        st.metric("ROI Calculado", f"{roi:.2f}%")
    else:
        st.info("No se encontraron picks con +EV hoy.")


