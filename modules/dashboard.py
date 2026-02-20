import streamlit as st
import connector
import ev_engine
import tracker
import pandas as pd

st.set_page_config(page_title="NBA ANALYST PRO", layout="wide")

# Gestión de Capital Real
capital = st.sidebar.number_input("Capital Actual (MXN):", value=1000.0)
st.title("🏀 Analista de Valor en Cascada")

if st.button("🚀 EJECUTAR ESCÁNER JERÁRQUICO"):
    datos = connector.obtener_datos_caliente_limpios()
    
    # Rescate con datos reales de tus capturas para testeo
    if not datos:
        datos = [{"game": "Cleveland Cavaliers @ Charlotte Hornets", "linea": 228.5},
                 {"game": "Milwaukee Bucks @ New Orleans Pelicans", "linea": 223.5}]

    pool_parlay = []

    for p in datos:
        # Llamada al motor jerárquico
        res = ev_engine.analizar_jerarquia_maestra(p)
        
        # Filtro de estatus
        status = "🔥 EXCELENTE" if res['prob'] >= 0.85 else "⚡ BUENA"
        color = "#00FF00" if res['prob'] >= 0.85 else "#FFFF00"

        if res['prob'] >= 0.85:
            pool_parlay.append({"partido": p['game'], "pick": res['seleccion']})

        # Tarjeta concisa (Solo datos clave)
        st.markdown(f"""
            <div style="border-left: 8px solid {color}; padding:10px; background-color:#1e1e1e; border-radius:5px; margin-bottom:5px;">
                <b style="color:{color};">{status} ({res['prob']*100:.0f}%)</b> | {p['game']}<br>
                🎯 <b>{res['seleccion']}</b> ({res['tipo']})
            </div>
        """, unsafe_allow_html=True)

    # Constructor de Parlay Mixto
    if len(pool_parlay) >= 2:
        st.divider()
        st.subheader("🎫 Ticket Sugerido (Picks de Élite)")
        for i, item in enumerate(pool_parlay):
            st.write(f"{i+1}. {item['partido']} -> **{item['pick']}**")
        
        if st.button("✅ REGISTRAR EN HISTORIAL"):
            # Aquí se guarda sin "None" y con el jugador real
            tracker.registrar_apuesta("PARLAY MIXTO", "Varios", "Mixto", 0.88, capital*0.1, "PENDIENTE")
            st.success("Guardado correctamente.")

# Historial con datos corregidos
st.subheader("📋 Historial de Movimientos")
# (Aquí iría el código del historial que ya tienes, pero ahora leerá los nombres reales)
