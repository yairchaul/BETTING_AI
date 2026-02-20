import streamlit as st
import connector
import ev_engine
import tracker
import os
import pandas as pd

st.set_page_config(page_title="NBA ELITE AI v16", layout="wide")

# Barra Lateral - Gestión de Capital
with st.sidebar:
    st.header("💵 Banca")
    capital = st.number_input("Capital Actual (MXN):", value=1000.0)
    st.divider()
    st.info("El sistema mezclará Puntos, Triples y Ganadores para el Parlay.")

st.title("🚀 Escáner Maestro Multimercado")

if st.button("🔥 EJECUTAR ANÁLISIS COMPLETO"):
    datos = connector.obtener_datos_caliente_limpios()
    
    # MODO RESCATE: Si la API no da datos, usamos una lista de prueba real
    if not datos:
        st.warning("API sin cuota o sin partidos. Cargando partidos clave para Testeo...")
        datos = [{"game": "Milwaukee Bucks @ Pelicans"}, {"game": "Brooklyn Nets @ Thunder"}, {"game": "LA Clippers @ Lakers"}]

    pool_parlay = []
    
    for p in datos:
        # Aquí se hace el análisis que suma todas las variables
        res = ev_engine.analizar_profundidad_maestra(p)
        
        # Filtrado de excelentes
        if res['prob'] >= 0.75:
            status, color = "🔥 EXCELENTE", "#00FF00"
            pool_parlay.append({"partido": p['game'], "pick": res['seleccion'], "prob": res['prob']})
        else:
            status, color = "⚠️ BAJA", "#FF4B4B"

        # Mostrar tarjeta de análisis
        st.markdown(f"""
            <div style="border-left: 8px solid {color}; padding:10px; background-color:#1e1e1e; margin-bottom:5px; border-radius:5px;">
                <h4 style="margin:0; color:{color};">{status} | {res['tipo']}</h4>
                <b>{p['game']}</b> -> {res['seleccion']} (Confianza: {res['prob']*100:.0f}%)
            </div>
        """, unsafe_allow_html=True)

    # --- SECCIÓN DEL PARLAY MIXTO ---
    if len(pool_parlay) >= 3:
        st.divider()
        st.success("🎯 PARLAY ÉLITE DETECTADO")
        
        monto = capital * 0.10
        cuota = 6.85 # Cuota promedio por 3 picks excelentes
        ganancia = (monto * cuota) - monto

        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📝 Ticket Sugerido")
            for i, pick in enumerate(pool_parlay[:3]):
                st.write(f"{i+1}. **{pick['partido']}**: {pick['pick']}")
        
        with col2:
            st.metric("Inversión (10%)", f"${monto:.2f} MXN")
            st.metric("Ganancia Neta", f"${ganancia:.2f} MXN", delta="ROI Potencial")
            
            # Registro en historial con el paréntesis corregido
            if st.button("✅ GUARDAR Y REGISTRAR APUESTA"):
                tracker.registrar_apuesta("PARLAY MIXTO", "Varios", "Varios", 0.85, monto, "PENDIENTE")
                st.balloons()

# --- HISTORIAL DE MOVIMIENTOS ---
st.subheader("📋 Últimos Movimientos Guardados")
if os.path.exists('historial_apuestas.csv'):
    df = pd.read_csv('historial_apuestas.csv')
    # Filtramos solo los que fueron excelentes en el historial
    st.dataframe(df.tail(10), use_container_width=True)
