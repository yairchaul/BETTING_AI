import streamlit as st
import ev_engine
import connector
import tracker

st.set_page_config(page_title="NBA Elite Scanner", layout="wide")

# Barra Lateral: Calculadora Dinámica
with st.sidebar:
    st.header("💵 Mi Carrito")
    capital_total = st.number_input("Capital Actual (MXN):", value=1000.0)
    cuota_parlay = st.number_input("Momio Total:", value=6.50)
    
    # La inversión total es el 10% del capital
    stake_total = capital_total * 0.10
    ganancia_neta = (stake_total * cuota_parlay) - stake_total
    
    st.divider()
    st.metric("Inversión Total", f"${stake_total:.2f}")
    st.metric("Ganancia Neta", f"${ganancia_neta:.2f}", delta=f"ROI {(cuota_parlay-1)*100:.0f}%")

st.title("🏀 Escáner Maestro Multicapa")

if st.button("🔍 ESCANEAR TODOS LOS PARTIDOS DE HOY"):
    # CONEXIÓN DINÁMICA: Obtiene todos los partidos sin filtros manuales
    partidos_hoy = connector.obtener_datos_reales()
    
    if not partidos_hoy:
        st.warning("No se detectaron partidos activos en la API.")
    else:
        st.write(f"✅ Analizando **{len(partidos_hoy)}** partidos encontrados...")
        
        # Stake por cada tarjeta (Inversión dividida equitativamente)
        stake_por_pick = stake_total / len(partidos_hoy)

        for p in partidos_hoy:
            res = ev_engine.analizar_jerarquia_por_partido(p)
            
            # Formato de Estatus
            es_top = res['confianza'] >= 0.80
            status_text = "🔥 EXCELENTE" if es_top else "⚡ BUENA"
            status_color = "#00FF00" if es_top else "#FFFF00"

            # INTERFAZ VISUAL COMPACTA (Estilo Ticket Caliente)
            st.markdown(f"""
                <div style="border: 1px solid #333; border-left: 6px solid {status_color}; padding: 10px; border-radius: 6px; background-color: #111; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.75em; color: gray; text-transform: uppercase;">{res['categoria']}</span>
                        <b style="font-size: 0.8em; color: {status_color};">{status_text} ({res['confianza']*100:.0f}%)</b>
                    </div>
                    <div style="margin: 4px 0;">
                        <div style="font-size: 0.85em; color: #aaa;">{res['partido']}</div>
                        <div style="font-size: 1.1em; font-weight: bold; color: white;">{res['seleccion']}</div>
                    </div>
                    <div style="text-align: right; font-size: 0.7em; color: gray; border-top: 1px solid #222; margin-top: 6px; padding-top: 4px;">
                        Análisis: {res['protagonista']} | Inversión: ${stake_por_pick:.2f} MXN
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Historial detallado por protagonista
            tracker.registrar_apuesta(res['partido'], res['protagonista'], res['seleccion'], res['confianza'], stake_por_pick, "PENDIENTE")
