import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker
import os

st.set_page_config(page_title="NBA ELITE - Parlay Builder Pro", layout="wide")

# Barra lateral para el capital
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
        for p in partidos:
            res = ev_engine.analizar_mejor_opcion(p)
            
            # Solo mostramos y guardamos picks excelentes
            if res['prob'] >= 0.75:
                pool_parlay.append({"game": p['game'], "pick": res['seleccion'], "prob": res['prob']})
                st.success(f"🔥 EXCELENTE: {p['game']} -> {res['seleccion']} ({res['prob']*100:.0f}%)")

        # --- SECCIÓN DE TICKET DE PARLAY ---
        if len(pool_parlay) >= 3:
            st.divider()
            st.subheader("🎫 TU PARLAY SUGERIDO")
            
            # Calculamos cuota aproximada y ganancia
            cuota = 6.0  # Cuota estimada para 3 favoritos
            monto_apuesta = capital * 0.10 # 10% del capital para el Parlay
            ganancia = (monto_apuesta * cuota) - monto_apuesta
            
            col1, col2 = st.columns(2)
            with col1:
                for i in range(3):
                    st.write(f"✅ {pool_parlay[i]['game']}: **{pool_parlay[i]['pick']}**")
            
            with col2:
                st.metric("Inversión Sugerida", f"${monto_apuesta:.2f}")
                st.metric("Ganancia Potencial", f"${ganancia:.2f}", delta="ROI +500%")
                
                # CORRECCIÓN DE LA LÍNEA 86
                if st.button("✅ REGISTRAR ESTA APUESTA"):
                    tracker.registrar_apuesta("PARLAY 3-WAY", "Varios", "Varios", 0.85, monto_apuesta, "PENDIENTE")
                    st.balloons()
                    st.info("Apuesta guardada en el historial.")
        else:
            st.info(f"Buscando más picks... Llevamos {len(pool_parlay)} de 3 requeridos para el Parlay.")

# Mostrar historial al final
st.subheader("📋 Historial de Movimientos")
if os.path.exists('historial_apuestas.csv'):
    st.dataframe(pd.read_csv('historial_apuestas.csv').tail(10), use_container_width=True)
