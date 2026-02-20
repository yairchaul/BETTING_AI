import streamlit as st
import ev_engine
import connector
import tracker

st.set_page_config(page_title="Ticket Pro", layout="wide")

# Calculadora de ROI en el Sidebar
with st.sidebar:
    st.header("💳 Mi Carrito")
    capital = st.number_input("Capital MXN:", value=1000.0)
    cuota = st.number_input("Momio/Cuota:", value=6.50)
    
    # Cálculos reales de Trading
    inversion_total = capital * 0.10 # Stake 10%
    ganancia_neta = (inversion_total * cuota) - inversion_total
    roi_porcentual = (cuota - 1) * 100

    st.divider()
    st.metric("Inversión Sugerida", f"${inversion_total:.2f}")
    st.metric("Ganancia Neta", f"${ganancia_neta:.2f}", delta=f"{roi_porcentual:.0f}% ROI")

st.title("🎫 Ticket de Apuestas NBA")

if st.button("🚀 GENERAR SELECCIONES DE VALOR"):
    datos = connector.obtener_datos_reales() # O datos de prueba si falla la API
    if not datos:
        datos = [{"id": "CLE@CHA", "linea": 228.5}]

    for p in datos:
        res = ev_engine.analizar_jerarquia_maestra(p)
        
        # Diseño Compacto Estilo Caliente
        status = "🔥 EXCELENTE" if res['confianza'] >= 0.85 else "⚡ BUENA"
        color = "#00e676" if res['confianza'] >= 0.85 else "#ffeb3b"

        st.markdown(f"""
            <div style="border: 1px solid #444; padding:12px; border-radius:8px; background-color:#1a1a1a; margin-bottom:8px; line-height:1.2;">
                <div style="display:flex; justify-content:space-between; font-size:0.75em; color:gray;">
                    <span>{res['mercado']}</span>
                    <span style="color:{color}; font-weight:bold;">{status} ({res['confianza']*100:.0f}%)</span>
                </div>
                <div style="margin:5px 0;">
                    <div style="font-size:0.85em; color:#bbb;">{res['partido']}</div>
                    <div style="font-size:1.1em; font-weight:bold; color:white;">{res['seleccion']}</div>
                </div>
                <div style="text-align:right; font-size:0.75em; color:gray; border-top:1px solid #333; padding-top:4px;">
                    Inversión por Pick: ${inversion_total/len(datos):.2f} MXN
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Registro en Historial Detallado
        tracker.registrar_apuesta(res['partido'], res['protagonista'], res['seleccion'], res['confianza'], inversion_total, "PENDIENTE")

    st.success(f"✅ Parlay armado. Retorno estimado: ${inversion_total * cuota:.2f} MXN")
