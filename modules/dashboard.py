import streamlit as st
import connector
import ev_engine

st.set_page_config(page_title="NBA Elite Scanner", layout="wide")

# Sidebar: Calculadora
with st.sidebar:
    st.header("💳 Gestión de Banca")
    capital = st.number_input("Capital MXN:", value=1000.0)
    inversion_total = capital * 0.10
    st.metric("Inversión Sugerida (10%)", f"${inversion_total:.2f}")

st.title("🏀 Escáner Maestro Multicapa")

if st.button("🔍 ESCANEAR PARTIDOS DE HOY"):
    # Solución al error de la imagen: Bloque de seguridad
    try:
        todos_los_partidos = connector.obtener_datos_reales()
        picks_finales = []

        for p in todos_los_partidos:
            resultado = ev_engine.analizar_jerarquia_por_partido(p)
            if resultado: # Solo si pasó el filtro del 70%
                picks_finales.append(resultado)

        if not picks_finales:
            st.error("❌ Ningún mercado superó el 70% de probabilidad hoy.")
        else:
            st.write(f"✅ Se encontraron **{len(picks_finales)}** picks de alta confianza.")
            
            # Reparto equitativo del capital
            stake_unid = inversion_total / len(picks_finales)

            for pick in picks_finales:
                # Interfaz Compacta Estilo Ticket
                color = "#00FF00" if pick['confianza'] >= 0.85 else "#FFFF00"
                st.markdown(f"""
                    <div style="border: 1px solid #444; border-left: 5px solid {color}; padding: 10px; border-radius: 6px; background-color: #111; margin-bottom: 5px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: {color};">
                            <b>{pick['categoria']}</b>
                            <b>{pick['confianza']*100:.1f}%</b>
                        </div>
                        <div style="font-size: 0.9em; color: #bbb;">{pick['partido']}</div>
                        <div style="font-size: 1.1em; font-weight: bold; color: white;">{pick['seleccion']}</div>
                        <div style="text-align: right; font-size: 0.7em; color: gray;">Sugerido: ${stake_unid:.2f} MXN</div>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error de conexión: {e}. Verifica que connector.py tenga la función obtener_datos_reales()")
