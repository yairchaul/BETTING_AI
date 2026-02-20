import streamlit as st
import ev_engine
import connector
import tracker

st.set_page_config(page_title="Ticket Pro NBA", layout="wide")

# Barra lateral: Calculadora de ROI Estilo Caliente
with st.sidebar:
    st.header("💵 Gestión de Banca")
    capital = st.number_input("Capital Disponible (MXN):", value=1000.0, step=100.0)
    cuota_parlay = st.number_input("Cuota Total (Momio):", value=6.50, step=0.1)
    
    # Cálculos de inversión
    stake_sugerido = capital * 0.10  # 10% de inversión
    ganancia_neta = (stake_sugerido * cuota_parlay) - stake_sugerido
    roi_final = (cuota_parlay - 1) * 100

    st.divider()
    st.metric("Inversión Sugerida", f"${stake_sugerido:.2f}")
    st.metric("Ganancia Neta", f"${ganancia_neta:.2f}", delta=f"{roi_final:.0f}% ROI")

st.title("🎫 Ticket de Valor Único")

if st.button("🚀 GENERAR TICKET"):
    # Prevención de AttributeError: verificamos que la función exista
    try:
        datos_api = connector.obtener_datos_reales()
    except AttributeError:
        # Datos de respaldo si el conector falla
        datos_api = [{"id": "CLE@CHA", "linea": 228.5}, {"id": "BKN@OKC", "linea": 213.5}]

    for p in datos_api:
        pick = ev_engine.analizar_jerarquia_maestra(p)
        
        # Diseño de Tarjeta Compacta (Estilo Ticket Caliente)
        status = "🔥 EXCELENTE" if pick['confianza'] >= 0.85 else "⚡ BUENA"
        color_borde = "#00FF00" if pick['confianza'] >= 0.85 else "#FFFF00"

        st.markdown(f"""
            <div style="border: 1px solid #444; border-left: 5px solid {color_borde}; padding: 10px; border-radius: 5px; background-color: #111; margin-bottom: 5px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                    <span style="font-size: 0.7em; color: gray;">{pick['mercado']}</span>
                    <b style="font-size: 0.75em; color: {color_borde};">{status} ({pick['confianza']*100:.0f}%)</b>
                </div>
                <div style="font-size: 0.8em; color: #ddd;">{pick['partido']}</div>
                <div style="font-size: 1.1em; font-weight: bold; color: #fff; margin-top: 2px;">{pick['seleccion']}</div>
                <div style="text-align: right; font-size: 0.65em; color: gray; border-top: 1px solid #222; margin-top: 5px; padding-top: 3px;">
                    Sugerido: ${stake_sugerido/len(datos_api):.2f} MXN
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Historial con nombres específicos (No etiquetas genéricas)
        tracker.registrar_apuesta(
            pick['partido'], 
            pick['protagonista'], 
            pick['seleccion'], 
            pick['confianza'], 
            stake_sugerido, 
            "PENDIENTE"
        )
