import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker
import os

st.set_page_config(page_title="NBA ELITE AI v15", layout="wide")

# --- BARRA LATERAL (Gestión de Capital) ---
with st.sidebar:
    st.header("💵 Gestión de Inversión")
    capital_total = st.number_input("Capital Disponible (MXN):", value=1000.0)
    estrategia = st.selectbox("Estrategia:", ["Independiente (Fijo)", "En Cadena (Parlay)"])
    st.divider()
    st.info("El sistema buscará Parlays de 3 partidos solo con estatus EXCELENTE.")

st.title("🏀 NBA ELITE - Parlay & Prop Scanner")

if st.button("🚀 EJECUTAR ANÁLISIS MAESTRO"):
    datos = connector.obtener_datos_caliente_limpios()
    pool_parlay = []
    
    if not datos:
        st.warning("No hay datos disponibles en este momento.")
    else:
        st.subheader(f"🔍 Escaneando Oportunidades para ${capital_total}")
        
        for p in datos:
            # El motor decide si el Over es bueno o si recalcula a Jugador/Ganador
            analisis = ev_engine.analizar_profundidad(p['home'], p['away'], p['linea'])
            
            prob = analisis['prob']
            # Definimos categorías
            if prob >= 0.75:
                status, color, pct = "🔥 EXCELENTE", "#00FF00", 0.05
                pool_parlay.append({"game": p['game'], "pick": analisis['seleccion'], "prob": prob})
            elif prob >= 0.60:
                status, color, pct = "⚡ BUENA", "#FFFF00", 0.02
            else:
                status, color, pct = "⚠️ BAJA", "#FF4B4B", 0.00
            
            monto_sugerido = capital_total * pct
            
            # Tarjetas Visuales Pro
            if status != "⚠️ BAJA":
                st.markdown(f"""
                <div style="border-left: 10px solid {color}; padding:15px; background-color:#1e1e1e; border-radius:10px; margin-bottom:10px">
                    <h3 style="color:{color}; margin:0;">{status}</h3>
                    <p style="margin:0;"><b>{p['game']}</b> | {analisis['nota']}</p>
                    <p style="margin:0; font-size:1.1em;">Selección: <b>{analisis['seleccion']}</b> | Invertir: <b>${monto_sugerido:.2f} MXN</b></p>
                </div>
                """, unsafe_allow_html=True)

        # --- SECCIÓN DE PARLAY ---
        st.divider()
        if len(pool_parlay) >= 3:
            st.success("🎯 PARLAY ÉLITE DETECTADO (3-WAY)")
            ticket = pool_parlay[:3]
            
            st.markdown(f"""
            <div style="background-color:#0e1117; border: 2px solid gold; padding:20px; border-radius:15px; text-align:center">
                <h2 style="color:gold;">🎫 TICKET SUGERIDO</h2>
                <p>1. {ticket[0]['game']} -> <b>{ticket[0]['pick']}</b></p>
                <p>2. {ticket[1]['game']} -> <b>{ticket[1]['pick']}</b></p>
                <p>3. {ticket[2]['game']} -> <b>{ticket[2]['pick']}</b></p>
                <hr>
                <h4 style="color:#00FF00;">Inversión Sugerida: ${capital_total * 0.10:.2f} MXN</h4>
            </div>
            """, unsafe_allow_html=True)
            # Aquí llamamos al bot de Telegram (opcional)
        else:
            st.info("Buscando más opciones 'Excelente' para armar un Parlay seguro...")

# --- HISTORIAL DETALLADO ---
st.subheader("📋 Historial de Movimientos")
if os.path.exists('historial_apuestas.csv'):
    df_hist = pd.read_csv('historial_apuestas.csv')
    st.dataframe(df_hist.tail(5), use_container_width=True)
