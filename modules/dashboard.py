import streamlit as st
import connector
import ev_engine

# --- CONFIGURACIÓN E INTERFAZ "TICKET PRO" ---
st.set_page_config(layout="wide")
st.sidebar.title("💵 Gestión de Banca")
capital = st.sidebar.number_input("Capital MXN:", value=1000.0)
cuota = st.sidebar.number_input("Cuota del Parlay:", value=6.50)

# Inversión Sugerida (10%)
stake_total = capital * 0.10
ganancia = (stake_total * cuota) - stake_total

st.sidebar.info(f"Inversión Sugerida: ${stake_total:.2f}")
st.sidebar.success(f"Ganancia Neta: ${ganancia:.2f} (ROI {(cuota-1)*100:.0f}%)")

st.title("🎫 Analista de Valor: Ticket Pro")

if st.button("🚀 INICIAR ESCÁNER MAESTRO"):
    # Conexión dinámica vía Selenium
    with st.spinner("Escaneando Caliente.mx en tiempo real..."):
        datos_reales = connector.obtener_datos_reales()
        picks_validos = []

        for p in datos_reales:
            resultado = ev_engine.analizar_capas_dinamicas(p)
            if resultado: # Solo si pasó el 70%
                picks_validos.append(resultado)

    if not picks_validos:
        st.warning("Ningún mercado real superó el 70% de confianza hoy.")
    else:
        for item in picks_finales:
            # Color dinámico por confianza
            color = "#00FF00" if item['pick']['prob'] > 0.85 else "#FFFF00"
            
            # Tarjeta compacta idéntica a la imagen image_32bd7c
            st.markdown(f"""
                <div style="border: 1px solid #333; border-left: 6px solid {color}; padding: 15px; background-color: #1a1a1a; border-radius: 8px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: {color}; font-weight: bold;">BUENA ({item['pick']['prob']*100:.0f}%)</span>
                        <span style="color: white; font-weight: bold;">{item['pick']['momio']}</span>
                    </div>
                    <h3 style="margin: 5px 0; color: white;">{item['partido']}</h3>
                    <p style="color: #ccc; margin: 0;">🎯 <b>{item['pick']['jugador']}</b> {item['pick']['linea']}</p>
                    <p style="font-size: 0.8em; color: gray;">Mercado: {item['pick']['categoria']} | Inversión: ${stake_total/len(picks_validos):.2f}</p>
                </div>
            """, unsafe_allow_html=True)
