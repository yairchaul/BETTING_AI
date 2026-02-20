import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker
import os

st.set_page_config(page_title="NBA ELITE - Parlay Builder Pro", layout="wide")

# Gestión de Capital en la barra lateral
with st.sidebar:
    st.header("💵 Gestión de Capital")
    capital = st.number_input("Capital Disponible (MXN):", value=1000.0)
    st.write(f"Tu stake sugerido (5%) es: **${capital * 0.05:.2f}**")

st.title("🏀 NBA ELITE - Parlay Builder Pro")

if st.button("🚀 INICIAR ESCÁNER MAESTRO"):
    partidos = connector.obtener_datos_caliente_limpios()
    pool_parlay = []
    
    if not partidos:
        st.warning("No se detectaron partidos activos. Revisa la conexión con la API.")
    else:
        # Escaneo y visualización de oportunidades
        for p in partidos:
            res = ev_engine.analizar_mejor_opcion(p)
            
            # Solo picks con probabilidad 'Excelente' entran al Parlay
            if res['prob'] >= 0.80:
                pool_parlay.append({"game": p['game'], "pick": res['seleccion'], "cuota": 1.90})
                
                st.markdown(f"""
                <div style="border-left: 10px solid #00FF00; padding:15px; background-color:#1e1e1e; border-radius:10px; margin-bottom:10px">
                    <h3 style="color:#00FF00; margin:0;">🔥 EXCELENTE ({res['prob']*100:.0f}%)</h3>
                    <p style="margin:5px 0;"><b>{p['game']}</b>: {res['seleccion']}</p>
                    <p style="margin:0; color:gray; font-size:0.9em;">{res['nota']}</p>
                </div>
                """, unsafe_allow_html=True)

        # --- GENERACIÓN DEL MEJOR PARLAY ---
        if len(pool_parlay) >= 3:
            st.divider()
            st.subheader("🎫 EL MEJOR PARLAY DETECTADO")
            
            monto_apuesta = capital * 0.10 # Invertimos el 10% en el Parlay
            cuota_total = 1.90 * 1.90 * 1.90 # Cuota aprox de 6.85
            ganancia_potencial = (monto_apuesta * cuota_total) - monto_apuesta
            
            col1, col2 = st.columns(2)
            with col1:
                for i, item in enumerate(pool_parlay[:3]):
                    st.write(f"{i+1}. {item['game']} ➡️ **{item['pick']}**")
            
            with col2:
                st.metric("Inversión Sugerida", f"${monto_apuesta:.2f}")
                st.metric("Ganancia Neta", f"${ganancia_potencial:.2f}", delta="ROI +585%")
                
                # Botón para guardar la apuesta
                if st.button("✅ REGISTRAR ESTE PARLAY"):
                    tracker.registrar_apuesta("PARLAY 3-WAY", "Varios", "Varios", 0.85, monto_apuesta, "PENDIENTE")
                    st.success("¡Apuesta ingresada y guardada en el historial!")
        else:
            st.info(f"Buscando más opciones... Llevamos {len(pool_parlay)} de 3 picks 'Excelente' requeridos.")

# Historial de Movimientos
st.subheader("📋 Historial de Movimientos")
if os.path.exists('historial_apuestas.csv'):
    df_hist = pd.read_csv('historial_apuestas.csv')
    st.dataframe(df_hist.tail(10), use_container_width=True)

