import streamlit as st
import ev_engine
import connector
import tracker
import pandas as pd

st.set_page_config(page_title="NBA Analyst Pro", layout="wide")

# --- CALCULADORA DE ROI DINÁMICA ---
with st.sidebar:
    st.header("💵 Gestión de Banca")
    capital_total = st.number_input("Capital Actual (MXN):", value=1000.0, step=100.0)
    cuota_parlay = st.number_input("Cuota Total (Caliente):", value=6.50, step=0.1)
    
    st.divider()
    # Función de cálculo de retorno
    monto_apuesta = capital_total * 0.10 # Stake sugerido 10%
    retorno_total = monto_apuesta * cuota_parlay
    ganancia_neta = retorno_total - monto_apuesta
    
    st.metric("Inversión Sugerida", f"${monto_apuesta:.2f}")
    st.metric("Ganancia Neta", f"${ganancia_neta:.2f}", delta=f"ROI {((cuota_parlay-1)*100):.0f}%")

st.title("🚀 Escáner de Decisión Jerárquica")

if st.button("🔍 INICIAR ANÁLISIS MAESTRO"):
    datos_partidos = connector.obtener_datos_caliente_limpios()
    
    # Rescate de datos para testeo
    if not datos_partidos:
        datos_partidos = [{"game": "Bucks @ Pelicans"}, {"game": "Cavaliers @ Hornets"}]

    picks_elite = []

    for p in datos_partidos:
        res = ev_engine.analizar_jerarquia_maestra(p)
        
        # Lógica de estatus basada en probabilidad
        es_excelente = res['confianza'] >= 0.85
        status = "🔥 EXCELENTE" if es_excelente else "⚡ BUENA"
        color = "#00FF00" if es_excelente else "#FFFF00"

        if es_excelente:
            picks_elite.append(res)

        # --- INTERFAZ DE TARJETAS DE VALOR ---
        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding:20px; background-color:#1e1e1e; border-radius:15px; margin-bottom:15px">
                <h2 style="color:{color}; margin:0;">{status} ({res['confianza']*100:.0f}%)</h2>
                <h4 style="margin:5px 0;">{res['game']}</h4>
                <p style="font-size:1.2em; margin:0;">Selección: <b>{res['label']}</b></p>
                <p style="color:gray; font-size:0.9em;">Mercado: {res['categoria']} | {res['observacion']}</p>
                <hr style="opacity:0.2">
                <p style="margin:0;">👉 <b>Inversión Sugerida: ${monto_apuesta / 3:.2f} MXN</b></p>
            </div>
        """, unsafe_allow_html=True)

    # --- REGISTRO EN HISTORIAL DETALLADO ---
    if len(picks_elite) >= 2:
        if st.button("✅ REGISTRAR PARLAY EN HISTORIAL"):
            for pick in picks_elite:
                # Guardamos la selección específica, no etiquetas genéricas
                tracker.registrar_apuesta(
                    pick['game'], 
                    pick['sujeto'], 
                    pick['label'], 
                    pick['confianza'], 
                    monto_apuesta / len(picks_elite), 
                    "PENDIENTE"
                )
            st.success("Ticket guardado con éxito.")
