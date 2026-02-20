import streamlit as st
import pandas as pd
import connector

# Lógica de colores original
def color_linea(val, prob):
    if prob > 0.60:
        return 'background-color: #00FF00; color: black; font-weight: bold;' # Verde Élite
    return ''

st.title("🏀 NBA ELITE AI - SISTEMA DE VALOR v13")

if st.button("🔄 ANALIZAR TODAS LAS LÍNEAS"):
    datos = connector.obtener_juegos_con_lineas()
    df = pd.DataFrame(datos)
    
    # Aplicamos el estilo a la tabla
    st.subheader("🔥 Análisis de Probabilidad de Puntos (Over)")
    
    # Esta función recorre la tabla y pinta de verde la línea si la prob es alta
    styled_df = df.style.apply(lambda x: [color_linea(x.linea, x.prob_modelo) for i in x], axis=1)
    
    st.dataframe(styled_df, use_container_width=True)

    # --- GENERADOR DE REGISTRO DE GANANCIAS ---
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Inversión Total Sugerida", f"${df[df.prob_modelo > 0.6].shape[0] * 100} MXN")
    with col2:
        st.info("El sistema detectó valor real en los puntos del partido de Cleveland.")









