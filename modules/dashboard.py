import streamlit as st
import connector
import ev_engine

st.title("🏀 Escáner NBA: Selenium Real-Time")

if st.button("🔍 ESCANEAR CALIENTE.MX"):
    # 1. Selenium abre el navegador y copia los nombres reales
    datos_vivos = connector.obtener_datos_reales()
    
    picks_finales = []
    for d in datos_vivos:
        res = ev_engine.analizar_jerarquia_maestra(d)
        if res: # Solo los que superan el 70%
            picks_finales.append(res)

    if not picks_finales:
        st.error("Ningún mercado real superó el 70% de probabilidad.")
    else:
        st.success(f"Se encontraron {len(picks_finales)} picks reales.")
        
        for item in picks_finales:
            # Tarjeta compacta estilo Caliente
            st.markdown(f"""
                <div style="border: 1px solid #444; border-left: 5px solid #00FF00; padding: 10px; background-color: #111;">
                    <b style="color: #FFFF00;">{item['pick']['prob']*100:.1f}% CONFIDENCIA</b>
                    <div style="color: white; font-size: 1.2em;">{item['pick']['seleccion']}</div>
                    <div style="color: gray;">{item['partido']}</div>
                    <div style="text-align: right; color: #00FF00;">Momio: {item['pick']['momio']}</div>
                </div>
            """, unsafe_allow_html=True)
