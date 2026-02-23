import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Ticket Pro IA", layout="wide")
engine = EVEngine()

st.title("🎯 Ticket Pro IA: Análisis Fútbol")
archivo = st.file_uploader("Sube tu captura de Caliente/Liga MX", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, use_container_width=True)
    
    if st.button("🚀 Iniciar Análisis en Cascada"):
        with st.spinner("🤖 Aplicando Capas de Inteligencia..."):
            # Usar la API de Cloud Vision (la de tu 1ra imagen) haría esto 100% exacto
            resultado_ia = analyze_betting_image(archivo)
            
            if resultado_ia and "juegos" in resultado_ia:
                picks = engine.analyze_matches(resultado_ia)
                
                # Mostrar Tarjetas Visuales
                for p in picks:
                    with st.container(border=True):
                        st.subheader(f"🏟️ {p['partido']}")
                        cols = st.columns(4)
                        for i, capa in enumerate(p['capas']):
                            cols[i].metric(capa['nivel'], capa['pick'], capa['prob'])
                
                # SECCIÓN DE RESUMEN PARA COPIAR
                st.divider()
                st.subheader("📝 Resumen para Compartir")
                texto_social = engine.generar_resumen_social(picks)
                st.text_area("Copia este texto:", texto_social, height=200)
                st.button("📋 Copiar al portapapeles (Simulado)")
            else:
                st.error("No se detectaron juegos. Revisa la imagen.")
