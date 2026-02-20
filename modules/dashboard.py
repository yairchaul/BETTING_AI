import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker
import os

st.set_page_config(page_title="NBA ELITE - Parlay Builder Pro", layout="wide")

# --- BARRA LATERAL: GESTIÓN DE DINERO ---
with st.sidebar:
    st.header("💵 Control de Capital")
    capital_usuario = st.number_input("Monto a Invertir (MXN):", value=1000.0, step=100.0)
    st.info("Solo los picks con probabilidad 'Excelente' (>75%) se usarán para armar el Parlay de 3 vías.")

st.title("🏀 NBA ELITE - Parlay & Prop Scanner")

# --- BOTÓN DE ESCANEO ---
if st.button("🚀 INICIAR ESCÁNER MAESTRO"):
    with st.spinner("Analizando mercados de Over, Ganadores y Jugadores..."):
        datos_api = connector.obtener_datos_caliente_limpios()
        pool_parlay = []

        if not datos_api:
            st.error("No se pudieron obtener datos. Revisa tu API Key o la conexión.")
        else:
            st.subheader(f"🔍 Análisis para tu Capital de ${capital_usuario}")
            
            for p in datos_api:
                # El motor elige la vía más certera (Puntos, Ganador o Prop de Jugador)
                analisis = ev_engine.analizar_mejor_opcion(p)
                
                prob = analisis['prob']
                # Categorización Visual
                if prob >= 0.75:
                    status, color, pct = "🔥 EXCELENTE", "#00FF00", 0.05
                    # Solo los excelentes entran al pool del parlay
                    pool_parlay.append({"partido": p['game'], "pick": analisis['seleccion'], "prob": prob})
                elif prob >= 0.60:
                    status, color, pct = "⚡ BUENA", "#FFFF00", 0.02
                else:
                    status, color, pct = "⚠️ BAJA", "#FF4B4B", 0.00

                # Cálculo de inversión individual
                monto_sugerido = capital_usuario * pct

                # Renderizado de Tarjeta Profesional
                if status != "⚠️ BAJA":
                    st.markdown(f"""
                    <div style="border-left: 10px solid {color}; padding:15px; background-color:#1e1e1e; border-radius:10px; margin-bottom:10px">
                        <h3 style="color:{color}; margin:0;">{status} ({prob*100:.0f}%)</h3>
                        <p style="margin:5px 0;"><b>{p['game']}</b></p>
                        <p style="margin:0;">Selección sugerida: <b>{analisis['seleccion']}</b></p>
                        <p style="margin:0; color:gray; font-size:0.9em;">{analisis['nota']}</p>
                        <hr style="opacity:0.2">
                        <p style="margin:0;">👉 Inversión sugerida: <b>${monto_sugerido:.2f} MXN</b></p>
                    </div>
                    """, unsafe_allow_html=True)

            # --- CONSTRUCTOR DE PARLAY DE 3 VÍAS ---
            st.divider()
            if len(pool_parlay) >= 3:
                st.success("🎯 TICKET DE PARLAY CONFIGURADO")
                ticket = pool_parlay[:3]
                
                # Simulamos cálculo de ganancia
                cuota_estimada = 6.50 # Cuota promedio para 3 picks favoritos
                monto_parlay = capital_usuario * 0.10 # Sugerimos el 10% para el parlay
                ganancia_total = monto_parlay * cuota_total
                
                st.markdown(f"""
                <div style="background-color:#0e1117; border: 2px solid gold; padding:20px; border-radius:15px;">
                    <h2 style="color:gold; text-align:center;">🎫 PARLAY ELITE DETECTADO</h2>
                    <p>1. {ticket[0]['partido']} ➡️ <b>{ticket[0]['pick']}</b></p>
                    <p>2. {ticket[1]['partido']} ➡️ <b>{ticket[1]['pick']}</b></p>
                    <p>3. {ticket[2]['partido']} ➡️ <b>{ticket[2]['pick']}</b></p>
                    <hr>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Inversión: <b>${monto_parlay:.2f} MXN</b></span>
                        <span style="color:#00FF00;">Ganancia Neta: <b>${(monto_parlay * cuota_estimada) - monto_parlay:.2f} MXN</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("💾 REGISTRAR PARLAY EN HISTORIAL"):
                    tracker.registrar_apuesta("PARLAY 3-WAY", "Varios", "Varios", 0.8
