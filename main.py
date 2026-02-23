import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración inicial
st.set_page_config(page_title="Ticket Pro IA", layout="wide")
engine = EVEngine()

# CSS Inyectado para reducir tamaño de textos y métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    h4 { font-size: 1rem !important; margin-bottom: 0px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Ticket Pro IA: Análisis Fútbol")

# REINSTALADA LA OPCIÓN DE SUBIR IMAGEN
archivo = st.file_uploader("Sube tu captura de Caliente/Liga MX", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, use_container_width=True)
    
    if st.button("🚀 Iniciar Análisis en Cascada", use_container_width=True):
        with st.spinner("🤖 Procesando imagen con Cloud Vision..."):
            resultado_ia = analyze_betting_image(archivo)
            
            if resultado_ia and "juegos" in resultado_ia:
                picks = engine.analyze_matches(resultado_ia)
                
                st.subheader("📊 Resultados del Análisis")
                
                # Diseño compacto de tarjetas
                for p in picks:
                    with st.container(border=True):
                        st.markdown(f"#### 🏟️ {p['partido']} | Momio: {p['momio']}")
                        cols = st.columns(4)
                        for i, capa in enumerate(p['capas']):
                            # Metric más pequeña gracias al CSS arriba
                            cols[i].metric(capa['nivel'], capa['pick'], capa['prob'])
                
                st.divider()
                st.subheader("📝 Resumen para Compartir")
                texto_social = engine.generar_resumen_social(picks)
                st.text_area("Copia este texto para tus grupos:", texto_social, height=150)
                st.button("📋 Copiar al portapapeles")
            else:
                st.error("Error: No se detectaron datos legibles. Intenta con una captura más clara.")
