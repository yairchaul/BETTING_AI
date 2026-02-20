# Añade esto al inicio de tu dashboard para probar
if st.sidebar.button("🔍 Testear Conexión"):
    test_data = connector.obtener_datos_caliente_limpios()
    if test_data:
        st.sidebar.success(f"Conexión OK: {len(test_data)} partidos encontrados.")
    else:
        st.sidebar.error("Conexión fallida. Revisa los Secrets.")
import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker
import os

st.set_page_config(page_title="NBA ELITE Pro", layout="wide")

# Barra lateral para gestión de banca
with st.sidebar:
    st.header("💵 Gestión de Capital")
    capital_mxn = st.number_input("Capital Disponible (MXN):", value=1000.0)
    st.write(f"Stake sugerido (5%): **${capital_mxn * 0.05:.2f}**")

st.title("🏀 NBA ELITE - Parlay Builder Pro")

if st.button("🚀 INICIAR ESCÁNER MAESTRO"):
    with st.spinner("Analizando mercados de puntos, jugadores y ganadores..."):
        partidos = connector.obtener_datos_caliente_limpios()
        pool_parlay = []

        if not partidos:
            st.warning("No se detectaron partidos activos. Verifica la conexión API.")
        else:
            # Mostramos los mejores picks individuales
            for p in partidos:
                res = ev_engine.analizar_mejor_opcion(p)
                if res['prob'] >= 0.80:
                    pool_parlay.append({"game": p['game'], "pick": res['seleccion'], "prob": res['prob']})
                    st.success(f"💎 **{p['game']}** -> {res['seleccion']} ({res['prob']*100:.0f}%)")

            # --- CONSTRUCTOR DEL PARLAY IDEAL ---
            if len(pool_parlay) >= 3:
                st.divider()
                st.subheader("🎫 TICKET DE PARLAY SUGERIDO")
                
                # Cálculo de ganancias para tu capital de $1000
                monto_apuesta = capital_mxn * 0.10 # Inversión del 10%
                cuota_estimada = 6.50 # Cuota promedio de 3 favoritos (aprox +550)
                ganancia_total = monto_apuesta * cuota_estimada
                
                col1, col2 = st.columns(2)
                with col1:
                    for i in range(3):
                        st.write(f"{i+1}. {pool_parlay[i]['game']} ➡️ **{pool_parlay[i]['pick']}**")
                
                with col2:
                    st.metric("Inversión Sugerida", f"${monto_apuesta:.2f} MXN")
                    st.metric("Ganancia Neta Est.", f"${ganancia_total - monto_apuesta:.2f} MXN", delta="ROI +550%")
                    
                    # CORRECCIÓN DE LA LÍNEA 86
                    if st.button("💾 REGISTRAR APUESTA INGRESADA"):
                        tracker.registrar_apuesta("PARLAY 3-WAY", "Varios", "Varios", 0.85, monto_apuesta, "PENDIENTE")
                        st.balloons()
                        st.info("Apuesta guardada correctamente en el historial.")
            else:
                st.info(f"Escaneo parcial: Se detectaron {len(pool_parlay)} de 3 picks 'Excelente' requeridos.")

# Historial de Movimientos actualizado
st.subheader("📋 Historial de Movimientos")
if os.path.exists('historial_apuestas.csv'):
    df_hist = pd.read_csv('historial_apuestas.csv')
    st.dataframe(df_hist.tail(10), use_container_width=True)


