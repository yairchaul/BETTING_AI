import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker

# --- PANEL DE CONTROL FINANCIERO ---
with st.sidebar:
    st.header("💵 Gestión de Inversión")
    capital_inicial = st.number_input("Monto a Invertir (MXN):", value=1000.0)
    metodo = st.selectbox("Estrategia:", ["Independiente (Fijo)", "En Cadena (Kelly)"])

# Corregimos el bloque 'if' que causaba el error
if st.button("🚀 EJECUTAR ESCÁNER Y CALCULAR STAKES"):
    # Aquí es donde el bloque debe estar sangrado correctamente
    datos_api = connector.obtener_datos_caliente_limpios()
    
    if not datos_api:
        st.warning("No se detectaron partidos activos en este momento.")
    else:
        st.subheader(f"🎯 Sugerencias para tu Capital de ${capital_inicial}")
        
        for p in datos_api:
            # Obtenemos la probabilidad real del motor
            prob = ev_engine.calcular_probabilidad_over(p['home'], p['away'], p['linea'])
            
            # Definimos el porcentaje de stake según la calidad del pick
            if prob >= 0.75:
                status, color, pct = "🔥 EXCELENTE", "#00FF00", 0.05 # 5% del capital
            elif prob >= 0.60:
                status, color, pct = "⚡ BUENA", "#FFFF00", 0.02    # 2% del capital
            else:
                status, color, pct = "⚠️ BAJA", "#FF4B4B", 0.00
            
            monto_apostado = capital_inicial * pct
            
            # Mostramos la tarjeta visual como en la v3.0
            if pct > 0:
                st.markdown(f"""
                <div style="border-left: 10px solid {color}; padding:15px; background-color:#1e1e1e; border-radius:10px; margin-bottom:10px">
                    <h3 style="color:{color}; margin:0;">{status}</h3>
                    <p style="margin:0;">Partido: {p['away']} @ {p['home']} | <b>Over {p['linea']}</b></p>
                    <p style="margin:0; font-size:1.2em;">👉 Invertir: <b>${monto_apostado:.2f} MXN</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                # REGISTRAMOS EN EL TRACKER
                tracker.registrar_apuesta(f"{p['away']}@{p['home']}", "Total", p['linea'], prob, monto_apostado, status)





