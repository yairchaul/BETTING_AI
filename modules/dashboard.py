import streamlit as st
import ev_engine
import connector
import tracker
import pandas as pd
import os

st.set_page_config(page_title="NBA ELITE AI - Jerarquía de Valor", layout="wide")

# Gestión de Inversión
with st.sidebar:
    st.header("💵 Calculadora de Ganancias")
    capital_usuario = st.number_input("Capital Disponible (MXN):", value=1000.0)
    cuota_caliente = st.number_input("Cuota del Parlay (Caliente):", value=6.50)

st.title("🚀 Analista Jerárquico Multimercado")

if st.button("🔥 EJECUTAR ESCÁNER Y CALCULAR RETORNO"):
    datos = connector.obtener_datos_caliente_limpios()
    
    # Rescate si la API no devuelve datos
    if not datos:
        datos = [{"game": "Cleveland Cavaliers @ Charlotte Hornets", "linea": 228.5},
                 {"game": "Milwaukee Bucks @ New Orleans Pelicans", "linea": 223.5},
                 {"game": "LA Clippers @ LA Lakers", "linea": 226.5}]

    picks_elite = []

    for p in datos:
        # El sistema evalúa todo y nos da el mejor pick de ese juego
        res = ev_engine.analizar_jerarquia_acumulativa(p)
        
        # Filtro de visualización (Verde si es >85%)
        color = "#00FF00" if res['prob'] >= 0.85 else "#FFFF00"
        
        if res['prob'] >= 0.85:
            picks_elite.append(res)

        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding:15px; background-color:#111; border-radius:10px; margin-bottom:10px">
                <h3 style="margin:0; color:{color};">Probabilidad: {res['prob']*100:.1f}%</h3>
                <b>Partido:</b> {p.get('game')}<br>
                <b>Mercado Ganador:</b> {res['seleccion']} ({res['tipo']})<br>
                <small style="color:gray;">Analizado: {res['jugador']}</small>
            </div>
        """, unsafe_allow_html=True)

    # --- FUNCIÓN DE CÁLCULO DE GANANCIAS ---
    if len(picks_elite) >= 2:
        st.divider()
        st.header("🎫 Ticket de Inversión Sugerido")
        
        stake_sugerido = capital_usuario * 0.10  # Invertimos el 10%
        ganancia_total = (stake_sugerido * cuota_caliente)
        ganancia_neta = ganancia_total - stake_sugerido

        col1, col2 = st.columns(2)
        with col1:
            st.write("### Estructura del Parlay")
            for pick in picks_elite[:3]:
                st.write(f"✅ {pick['jugador']}: **{pick['seleccion']}**")
        
        with col2:
            st.metric("Inversión (Stake)", f"${stake_sugerido:.2f} MXN")
            st.metric("Ganancia Neta Estimada", f"${ganancia_neta:.2f} MXN", delta=f"ROI {((cuota_caliente-1)*100):.0f}%")

            if st.button("✅ GUARDAR EN HISTORIAL"):
                tracker.registrar_apuesta("PARLAY JERÁRQUICO", "Varios", "Mixto", 0.90, stake_sugerido, "PENDIENTE")
                st.success("Ticket registrado con éxito.")

# Historial corregido (Sin "Total" genérico)
st.subheader("📋 Historial de Movimientos")
if os.path.exists('historial_apuestas.csv'):
    df_hist = pd.read_csv('historial_apuestas.csv')
    st.dataframe(df_hist.tail(10), use_container_width=True)
