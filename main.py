import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Ticket Pro IA", layout="wide")

# Inicialización segura
if 'engine' not in st.session_state:
    st.session_state.engine = EVEngine(st.secrets["GOOGLE_API_KEY"], st.secrets["GOOGLE_CSE_ID"])

st.title("🎯 Parlay Maestro: Análisis Dinámico")

archivo = st.file_uploader("Sube tu captura de Caliente/Liga MX", type=['png', 'jpg', 'jpeg'])

if archivo:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(archivo, width=250, caption="Captura")
    
    with col2:
        if st.button("🚀 GENERAR EL MEJOR PARLAY"):
            try:
                # Definición de la variable para evitar NameError
                with st.spinner("Analizando equipos y buscando rachas reales..."):
                    resultado_ia = analyze_betting_image(archivo)
                    todos, parlay = st.session_state.engine.analyze_matches(resultado_ia)
                
                if parlay:
                    st.success("🔥 MEJOR PARLAY DE LA SEMANA")
                    for p in parlay:
                        st.info(f"✅ **{p['partido']}** | Pick: `{p['pick']}` (Confianza: {p['victoria']})")
                
                with st.expander("Ver desglose detallado"):
                    for t in todos:
                        st.write(f"🏟️ {t['partido']} | Prob. Goles HT: {t['goles_ht']}")
            except Exception as e:
                st.error(f"Error en el proceso: {e}")
