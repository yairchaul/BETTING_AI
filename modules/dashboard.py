import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker # <--- Nuevo import

st.set_page_config(page_title="NBA ELITE TRACKER", layout="wide")

# --- CAPITAL ---
with st.sidebar:
    st.header("💳 Control de Caja")
    capital = st.number_input("Capital Actual (MXN):", value=1000.0)

if st.button("🔄 ESCANEAR Y REGISTRAR ELITES"):
    datos = connector.obtener_datos_caliente_limpios()
    
    for p in datos:
        # Probabilidad calculada por promedios (ev_engine)
        prob = ev_engine.calcular_probabilidad_over(p['home'], p['away'], p['linea'])
        
        # Recuperamos la esencia de las etiquetas
        if prob >= 0.65:
            status = "🔥 EXCELENTE"
            color = "#00FF00"
            stake = capital * 0.05 # Invertimos el 5% en excelentes
            
            # REGISTRO AUTOMÁTICO EN EXCEL/CSV
            tracker.registrar_apuesta(f"{p['away']}@{p['home']}", "Equipo Total", p['linea'], prob, stake, status)
            st.success(f"Registrada Sugerencia Élite: {p['away']} @ {p['home']} (Over {p['linea']})")
        
        elif prob >= 0.58:
            status = "⚡ BUENA"
            color = "#FFFF00"
            stake = capital * 0.02 # Invertimos el 2% en buenas
        else:
            status = "⚠️ BAJA"
            color = "#FF4B4B"
            stake = 0

# --- MOSTRAR HISTORIAL REAL ---
st.divider()
st.subheader("📋 Historial de Inversiones (Tracker)")
if os.path.exists('historial_apuestas.csv'):
    historial_df = pd.read_csv('historial_apuestas.csv')
    st.dataframe(historial_df.tail(10), use_container_width=True) # Muestra las últimas 10
else:
    st.info("Aún no hay apuestas registradas hoy.")










