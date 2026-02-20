import streamlit as st
import ev_engine
import connector

# Configuración de banca en sidebar
with st.sidebar:
    st.header("💰 Banca")
    capital = st.number_input("Capital MXN:", value=1000.0)
    cuota = st.number_input("Momio/Cuota Parlay:", value=6.50)
    
    # Cálculo de ROI estilo Caliente
    inversion = capital * 0.10 # Stake 10%
    ganancia_neta = (inversion * cuota) - inversion
    
    st.divider()
    st.metric("Inversión Sugerida", f"${inversion:.2f}")
    st.metric("Ganancia Neta", f"${ganancia_neta:.2f}", delta=f"ROI {((cuota-1)*100):.0f}%")

st.title("🎫 Analista de Valor: Ticket Pro")

if st.button("🚀 GENERAR TICKET"):
    datos = connector.obtener_datos_reales() # O datos de respaldo
    
    if not datos:
        datos = [{"game_id": "CLE@CHA", "linea": 228.5}]

    # Contenedor pequeño para las tarjetas
    for p in datos:
        res = ev_engine.analizar_jerarquia_maestra(p)
        status = "🔥 EXCELENTE" if res['prob'] >= 0.85 else "⚡ BUENA"
        color = "#00FF00" if res['prob'] >= 0.85 else "#FFFF00"

        # Diseño de tarjeta compacta (CSS Inline para evitar imágenes gigantes)
        st.markdown(f"""
            <div style="border: 1px solid #333; padding:10px; border-radius:5px; background-color:#111; margin-bottom:5px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:{color}; font-weight:bold; font-size:0.8em;">{status} ({res['prob']*100:.0f}%)</span>
                    <span style="color:gray; font-size:0.7em;">ID: NBA-0220</span>
                </div>
                <div style="margin:5px 0;">
                    <b style="font-size:0.9em;">{res['partido']}</b><br>
                    <span style="color:#00e676; font-size:1em;">🎯 {res['seleccion']}</span>
                </div>
                <div style="font-size:0.7em; color:gray; border-top:1px solid #222; padding-top:5px;">
                    Analizado: {res['jugador']} | Inversión: ${inversion/len(datos):.2f} MXN
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Resumen final de Parlay
    st.markdown(f"""
        <div style="background-color:#0d47a1; padding:10px; border-radius:5px; margin-top:10px; text-align:center;">
            <b>💰 TOTAL PARLAY: ${inversion:.2f} ⮕ Ganancia: ${(inversion*cuota):.2f}</b>
        </div>
    """, unsafe_allow_html=True)

