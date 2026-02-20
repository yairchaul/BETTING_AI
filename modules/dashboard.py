
import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker
import os

st.set_page_config(page_title="NBA ELITE AI - Parlay Builder", layout="wide")

# Barra Lateral: Gestión de Banca
with st.sidebar:
    st.header("💵 Gestión de Banca")
    capital_base = st.number_input("Capital Actual (MXN):", value=1000.0)
    st.write(f"Inversión sugerida (10%): **${capital_base * 0.10:.2f}**")

st.title("🚀 Escáner Maestro Multimercado")

if st.button("🔥 EJECUTAR ANÁLISIS COMPLETO"):
    # Obtenemos datos y manejamos el error de "no detectados"
    datos_crudos = connector.obtener_datos_caliente_limpios()
    
    # Simulacro de seguridad si la API está vacía o sin cuota
    if not datos_crudos:
        st.warning("API sin datos. Usando partidos clave del sistema para el Parlay...")
        datos_crudos = [{"game": "Milwaukee Bucks @ New Orleans Pelicans"}, 
                        {"game": "Brooklyn Nets @ Oklahoma City Thunder"}, 
                        {"game": "Los Angeles Clippers @ Los Angeles Lakers"}]

    pool_excelentes = []
    
    for p in datos_crudos:
        # Llamada corregida para evitar AttributeError
        res = ev_engine.analizar_profundidad_maestra(p)
        
        # Filtrado real de picks excelentes (>75%)
        if res['prob'] >= 0.75:
            pool_excelentes.append({"partido": p.get('game'), "pick": res['seleccion'], "prob": res['prob']})
            color = "#00FF00"
            status = "🔥 EXCELENTE"
        else:
            color = "#FFFF00"
            status = "⚡ BUENA"

        st.markdown(f"""
            <div style="border-left: 8px solid {color}; padding:10px; background-color:#1e1e1e; margin-bottom:5px; border-radius:5px;">
                <h4 style="margin:0; color:{color};">{status} | {res['tipo']}</h4>
                <b>{p.get('game')}</b> -> {res['seleccion']} (Confianza: {res['prob']*100:.0f}%)
            </div>
        """, unsafe_allow_html=True)

    # --- CONSTRUCCIÓN DEL PARLAY ---
    if len(pool_excelentes) >= 3:
        st.divider()
        st.subheader("🎫 TU MEJOR PARLAY (3-WAY)")
        
        monto_apuesta = capital_base * 0.10
        cuota_parlay = 6.50 # Cuota estimada para 3 favoritos
        ganancia_neta = (monto_apuesta * cuota_parlay) - monto_apuesta
        
        col1, col2 = st.columns(2)
        with col1:
            for i in range(3):
                st.write(f"{i+1}. **{pool_excelentes[i]['partido']}**: {pool_excelentes[i]['pick']}")
        
        with col2:
            st.metric("Monto a Invertir", f"${monto_apuesta:.2f} MXN")
            st.metric("Ganancia Estimada", f"${ganancia_neta:.2f} MXN", delta="ROI +550%")
            
            # Botón de registro con sintaxis corregida
            if st.button("✅ REGISTRAR ESTA APUESTA"):
                tracker.registrar_apuesta("PARLAY MIXTO", "Varios", "Varios", 0.85, monto_apuesta, "PENDIENTE")
                st.success("Apuesta guardada en el historial.")
    else:
        st.info(f"Escaneo parcial: Se detectaron {len(pool_excelentes)} de 3 picks 'Excelente' requeridos.")

# --- HISTORIAL ---
st.divider()
st.subheader("📋 Historial de Movimientos")
if os.path.exists('historial_apuestas.csv'):
    df_hist = pd.read_csv('historial_apuestas.csv')
    st.dataframe(df_hist.tail(10), use_container_width=True)


