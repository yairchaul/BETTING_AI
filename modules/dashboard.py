import streamlit as st
import connector
import ev_engine
import tracker
import os
import pandas as pd

st.set_page_config(page_title="NBA ELITE AI v17", layout="wide")

# Gestión de Banca (Sidebar)
capital = st.sidebar.number_input("Capital para Inversión (MXN):", value=1000.0)
st.sidebar.info(f"Estrategia: 10% Stake para Parlays de Élite.")

st.title("🏀 Escáner Maestro Multimercado")

if st.button("🚀 INICIAR ESCÁNER Y ARMAR PARLAY"):
    datos = connector.obtener_datos_caliente_limpios()
    
    # Rescate si la API no tiene juegos (Modo Test con tus imágenes)
    if not datos:
        datos = [
            {"game": "Golden State Warriors @ Kings", "linea": 235.5},
            {"game": "Milwaukee Bucks @ Pelicans", "linea": 228.0},
            {"game": "Cleveland Cavaliers @ Hornets", "linea": 220.5}
        ]

    picks_parlay = []

    for p in datos:
        # Llamamos al motor que ahora suma todas las opciones
        res = ev_engine.analizar_profundidad_maestra(p)
        
        # Filtro EXCELENTE (>75%)
        es_excelente = res['prob'] >= 0.75
        color = "#00FF00" if es_excelente else "#FFFF00"
        status = "🔥 EXCELENTE" if es_excelente else "⚡ BUENA"

        if es_excelente:
            picks_parlay.append({"game": p['game'], "pick": res['seleccion'], "jugador": res['jugador']})

        # Tarjeta Visual Mejorada
        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding:15px; background-color:#1e1e1e; border-radius:10px; margin-bottom:10px">
                <h3 style="color:{color}; margin:0;">{status} ({res['prob']*100:.0f}%)</h3>
                <p style="margin:5px 0;"><b>{p['game']}</b></p>
                <p style="margin:0;">🎯 Selección: <b>{res['seleccion']}</b> | Mercado: {res['tipo']}</p>
                <p style="color:gray; font-size:0.85em;">{res['nota']}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- CONSTRUCTOR DE PARLAY (3-WAY MIXTO) ---
    if len(picks_parlay) >= 3:
        st.divider()
        st.header("🎫 PARLAY ÉLITE DETECTADO")
        
        monto_ticket = capital * 0.10
        retorno = monto_ticket * 6.50 # Cuota estimada combinada

        col1, col2 = st.columns(2)
        with col1:
            for i, item in enumerate(picks_parlay[:3]):
                st.write(f"{i+1}. {item['game']} ➡️ **{item['pick']}**")
        
        with col2:
            st.metric("Inversión Sugerida", f"${monto_ticket:.2f} MXN")
            st.metric("Retorno Estimado", f"${retorno:.2f} MXN")
            
            # Registro en historial con DATOS REALES (Sin "Varios")
            if st.button("✅ REGISTRAR TICKET EN HISTORIAL"):
                for t in picks_parlay[:3]:
                    tracker.registrar_apuesta(t['game'], t['jugador'], t['pick'], 0.85, monto_ticket/3, "PENDIENTE")
                st.success("¡Parlay registrado con éxito!")
    else:
        st.info(f"Buscando más opciones... Detectados {len(picks_parlay)} de 3 picks necesarios.")

# Mostrar Historial (Sin errores de str/int)
st.subheader("📋 Historial de Movimientos")
if os.path.exists('historial_apuestas.csv'):
    df_hist = pd.read_csv('historial_apuestas.csv')
    st.dataframe(df_hist.tail(10), use_container_width=True)
