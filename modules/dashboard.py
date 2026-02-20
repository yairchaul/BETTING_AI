import streamlit as st
import connector
import ev_engine
import tracker

st.title("🏀 NBA ELITE - Parlay Builder Pro")

with st.sidebar:
    capital = st.number_input("Capital MXN", value=1000.0)
    st.info("Solo picks 'Excelente' (>75%) entrarán al Parlay.")

if st.button("🚀 INICIAR ESCÁNER MAESTRO"):
    partidos = connector.obtener_datos_caliente_limpios()
    pool_parlay = []
    
    for p in partidos:
        opcion = ev_engine.analizar_mejor_opcion(p)
        
        # Estética de tarjetas
        color = "#00FF00" if opcion['prob'] >= 0.75 else "#FFFF00"
        status = "🔥 EXCELENTE" if opcion['prob'] >= 0.75 else "⚡ BUENA"
        
        if opcion['prob'] >= 0.75:
            pool_parlay.append({"game": p['game'], "pick": opcion['seleccion'], "cuota": 1.91})
            
        st.markdown(f"""
        <div style="border-left: 10px solid {color}; padding:15px; background-color:#1e1e1e; border-radius:10px; margin-bottom:10px">
            <h3 style="color:{color}; margin:0;">{status}</h3>
            <p><b>{p['game']}</b>: {opcion['seleccion']}</p>
            <p style="font-size:0.9em; color:gray;">{opcion['nota']}</p>
        </div>
        """, unsafe_allow_html=True)

    # SECCIÓN DE PARLAY
    if len(pool_parlay) >= 3:
        st.divider()
        st.subheader("🎫 TICKET ELITE DETECTADO")
        
        monto_apuesta = capital * 0.10 # Sugerimos el 10% del capital para el parlay
        cuota_total = 1.91 * 1.91 * 1.91 # Ejemplo de cuota de 3 partidos
        ganancia_neta = (monto_apuesta * cuota_total) - monto_apuesta
        
        col1, col2 = st.columns(2)
        with col1:
            for i, pick in enumerate(pool_parlay[:3]):
                st.write(f"{i+1}. {pick['game']} -> **{pick['pick']}**")
        
        with col2:
            st.metric("Inversión", f"${monto_apuesta:.2f} MXN")
            st.metric("Ganancia Estimada", f"${ganancia_neta:.2f} MXN", delta="POTENCIAL")
            
            if st.button("✅ REGISTRAR APUESTA INGRESADA"):
                tracker.registrar_apuesta("PARLAY ELITE", "Multi", "Varios", 0.80, monto_apuesta, "PENDIENTE")
                st.success("Apuesta guardada en el historial.")

