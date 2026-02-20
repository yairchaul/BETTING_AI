import streamlit as st
import pandas as pd
import connector
import ev_engine
import tracker
import os

st.set_page_config(page_title="NBA ELITE AI - Multimercado", layout="wide")

# Gestión de capital de $1000
capital = st.sidebar.number_input("Capital Actual (MXN):", value=1000.0)
st.title("🚀 Escáner de Valor Multicapa")

if st.button("🔥 EJECUTAR ANÁLISIS MAESTRO"):
    datos_api = connector.obtener_datos_caliente_limpios()
    
    # Rescate en caso de que la API esté vacía
    if not datos_api:
        datos_api = [{"game": "Milwaukee Bucks @ Pelicans"}, {"game": "Cleveland Cavaliers @ Hornets"}]

    picks_excelentes = []

    for p in datos_api:
        # El motor ahora nos da el "Pick Ganador" de ese partido entre todas las opciones
        res = ev_engine.analizar_profundidad_maestra(p)
        
        # Filtro visual de estatus
        es_elite = res['prob'] >= 0.75
        color = "#00FF00" if es_elite else "#FFFF00"
        status = "🔥 EXCELENTE" if es_elite else "⚠️ BUENA"

        if es_elite:
            picks_excelentes.append({"game": p.get('game'), "res": res})

        # Renderizado de tarjeta sin errores de llave
        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding:15px; background-color:#1e1e1e; border-radius:10px; margin-bottom:10px">
                <h3 style="color:{color}; margin:0;">{status} ({res['prob']*100:.0f}%)</h3>
                <p style="font-size:1.1em; margin:5px 0;"><b>Partido:</b> {p.get('game')}</p>
                <p style="margin:0;"><b>Mejor Mercado Detectado:</b> {res['sel']} ({res['tipo']})</p>
                <p style="color:gray;">Analizando: {res['jug']}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- CONSTRUCTOR DE PARLAY CON LO MEJOR DE CADA MUNDO ---
    if len(picks_excelentes) >= 2:
        st.success(f"🎯 Se encontraron {len(picks_excelentes)} oportunidades de Élite.")
        monto = capital * 0.10
        
        if st.button("✅ REGISTRAR PARLAY EN HISTORIAL"):
            for item in picks_excelentes:
                # Guardamos con el nombre real del jugador o equipo analizado
                tracker.registrar_apuesta(item['game'], item['res']['jug'], item['res']['sel'], item['res']['prob'], monto/len(picks_excelentes), "PENDIENTE")
            st.balloons()

# --- HISTORIAL REALISTA ---
st.subheader("📋 Historial de Movimientos (Control de Filtros)")
if os.path.exists('historial_apuestas.csv'):
    df = pd.read_csv('historial_apuestas.csv')
    # Aquí verás nombres de jugadores cuando sea prop, o "Equipo" cuando sea over
    st.dataframe(df.tail(10), use_container_width=True)
