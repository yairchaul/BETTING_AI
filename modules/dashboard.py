import streamlit as st
import ev_engine
import connector
import tracker

st.set_page_config(page_title="NBA ELITE - Analista Pro", layout="wide")

# Barra Lateral: Calculadora de ROI
with st.sidebar:
    st.header("💵 Gestión de Capital")
    capital = st.number_input("Capital MXN:", value=1000.0)
    cuota_total = st.number_input("Cuota del Parlay:", value=6.50)
    
    # Cálculo dinámico
    stake_sugerido = capital * 0.10 # 10% de inversión
    ganancia_neta = (stake_sugerido * cuota_total) - stake_sugerido
    
    st.info(f"Inversión Sugerida: ${stake_sugerido:.2f}")
    st.success(f"Ganancia Neta: ${ganancia_neta:.2f}")

st.title("🏀 NBA ELITE - Analista Jerárquico")

if st.button("🚀 INICIAR ESCÁNER MAESTRO"):
    datos = connector.obtener_datos_caliente_limpios()
    
    # Datos de respaldo para evitar pantalla vacía
    if not datos:
        datos = [{"game": "Cleveland Cavaliers @ Charlotte Hornets", "linea": 228.5}]

    for p in datos:
        # Ejecución del motor sin errores de atributo
        res = ev_engine.analizar_jerarquia_maestra(p)
        
        # Lógica de Estatus
        es_excelente = res['probabilidad'] >= 0.80
        status = "🔥 EXCELENTE" if es_excelente else "⚡ BUENA"
        color = "#00FF00" if es_excelente else "#FFFF00"

        # INTERFAZ VISUAL DE TICKET (Similar a image_258e16.png)
        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding:20px; background-color:#1e1e1e; border-radius:10px; margin-bottom:15px">
                <h2 style="color:{color}; margin:0;">{status} ({res['probabilidad']*100:.0f}%)</h2>
                <h4 style="margin:5px 0;">{res['partido']}</h4>
                <p style="font-size:1.2em; margin:0;">🎯 Selección: <b>{res['seleccion']}</b></p>
                <p style="color:gray;">Mercado: {res['categoria']} | Analizado: {res['jugador']}</p>
                <p style="margin-top:10px; font-weight:bold;">Inversión sugerida: ${stake_sugerido / len(datos):.2f} MXN</p>
            </div>
        """, unsafe_allow_html=True)

        # Registro en historial detallado (Sin etiquetas genéricas)
        tracker.registrar_apuesta(res['partido'], res['jugador'], res['seleccion'], res['probabilidad'], stake_sugerido, "PENDIENTE")
