import streamlit as st
import connector
import ev_engine
import tracker

st.set_page_config(page_title="Ticket Pro NBA", layout="wide")

# Sidebar: Calculadora de ROI
with st.sidebar:
    st.header("💳 Mi Banca")
    capital = st.number_input("Capital Actual (MXN):", value=1000.0)
    cuota_parlay = st.number_input("Cuota/Momio Total:", value=6.50)
    
    # Inversión del 10%
    stake_total = capital * 0.10
    ganancia_neta = (stake_total * cuota_parlay) - stake_total
    
    st.divider()
    st.metric("Inversión Sugerida", f"${stake_total:.2f}")
    st.metric("Ganancia Neta", f"${ganancia_neta:.2f}", delta=f"ROI {(cuota_parlay-1)*100:.0f}%")

st.title("🎫 Ticket de Apuestas Caliente")

if st.button("🔍 EJECUTAR ANÁLISIS MAESTRO"):
    try:
        partidos = connector.obtener_datos_reales() # Conexión dinámica
        picks_validos = []

        for p in partidos:
            res = ev_engine.analizar_jerarquia_por_partido(p)
            if res: # Solo si pasó el umbral del 70%
                picks_validos.append(res)

        if not picks_validos:
            st.warning("⚠️ Ningún mercado superó el 70% de confianza hoy.")
        else:
            # Dividir inversión equitativamente
            stake_unid = stake_total / len(picks_validos)

            for pick in picks_validos:
                # Interfaz Compacta Estilo Caliente
                color = "#00FF00" if pick['confianza'] >= 0.85 else "#FFFF00"
                st.markdown(f"""
                    <div style="border: 1px solid #444; border-left: 4px solid {color}; padding: 8px; border-radius: 4px; background-color: #111; margin-bottom: 5px; line-height: 1.2;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.7em; color: gray;">
                            <span>{pick['categoria']}</span>
                            <b style="color: {color};">{pick['confianza']*100:.1f}% CONFIDENCIA</b>
                        </div>
                        <div style="font-size: 0.8em; color: #aaa; margin: 2px 0;">{pick['partido']}</div>
                        <div style="font-size: 1em; font-weight: bold; color: white;">{pick['seleccion']}</div>
                        <div style="text-align: right; font-size: 0.65em; color: #777; border-top: 1px solid #222; margin-top: 4px; padding-top: 2px;">
                            Inversión: ${stake_unid:.2f} MXN
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Registro en historial con nombre real del jugador
                tracker.registrar_apuesta(pick['partido'], pick['jugador'], pick['seleccion'], pick['confianza'], stake_unid, "PENDIENTE")

            st.success(f"✅ Ticket Generado con {len(picks_validos)} picks de élite.")

    except Exception as e:
        st.error(f"Error técnico: {e}")
