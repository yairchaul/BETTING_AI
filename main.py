import streamlit as st
import json
import os
import pandas as pd
from modules.vision_reader import analyze_betting_image
from modules.tracker import guardar_pick_automatico

st.set_page_config(page_title="Ticket Pro IA", layout="wide")

# --- INTERFAZ DE PESTAÑAS ---
tab1, tab2 = st.tabs(["🔥 Scanner de Mercados", "📜 Historial de Picks"])

with tab1:
    st.title("🏀 Vision Terminal")
    archivo = st.file_uploader("Sube captura de Caliente.mx", type=['png', 'jpg', 'jpeg'], key="uploader_principal")

    if archivo:
        st.image(archivo, width=500)
        
        # Agregamos un 'key' único para evitar el error StreamlitDuplicateElementId
        if st.button("🚀 Analizar Mercados", key="btn_analisis_unico"):
            with st.spinner("🤖 Procesando imagen..."):
                datos = analyze_betting_image(archivo)
                
                if datos and "juegos" in datos:
                    st.success(f"✅ Detectados {len(datos['juegos'])} juegos")
                    
                    # Espacios organizados para resultados
                    for idx, j in enumerate(datos["juegos"]):
                        with st.container(border=True):
                            c1, c2, c3 = st.columns([2,1,1])
                            c1.subheader(f"{j.get('away')} @ {j.get('home')}")
                            c2.metric("Línea/Total", j.get('handicap', j.get('total', 'N/A')))
                            c3.metric("Momio", j.get('moneyline', 'N/A'))
                            
                            # Guardar automáticamente cada juego detectado
                            guardar_pick_automatico(j, 0.05, 100.0)
                else:
                    st.error("No se pudo extraer JSON válido. Revisa la consola.")

with tab2:
    st.header("Historial de Análisis")
    if os.path.exists("data/picks.csv"):
        df = pd.read_csv("data/picks.csv")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("El historial aparecerá aquí después de tu primer análisis.")
