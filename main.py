import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Ticket Pro IA", layout="wide")

# Configura tus llaves de Google Cloud aquí
API_KEY = "TU_API_KEY"
CSE_ID = "TU_CX_ID"

engine = EVEngine(API_KEY, CSE_ID)

st.title("🎯 Parlay Maestro: Datos Reales")

archivo = st.file_uploader("Sube tu captura de Caliente/Liga MX", type=['png', 'jpg'])

if archivo:
    col_img, col_info = st.columns([1, 2])
    with col_img:
        # Imagen compacta para evitar scroll
        st.image(archivo, width=250, caption="Captura")
    
    with col_info:
        if st.button("🚀 ANALIZAR Y CREAR PARLAY", use_container_width=True):
            with st.spinner("Buscando datos reales en Google..."):
                try:
                    # Lector de Cloud Vision
                    resultado_ia = analyze_betting_image(archivo)
                    todos, parlay = engine.analyze_matches(resultado_ia)
                    
                    if parlay:
                        st.success("🔥 MEJOR PARLAY SUGERIDO")
                        with st.container(border=True):
                            for p in parlay:
                                st.write(f"✅ **{p['partido']}** ➔ `{p['pick']}` ({p['victoria']})")
                    
                    with st.expander("Ver Análisis en Cascada Completo"):
                        for t in todos:
                            st.write(f"🏟️ {t['partido']} | Prob. Goles HT: {t['goles_ht']}")
                except Exception as e:
                    st.error(f"Falta configurar librerías o llaves: {e}")


