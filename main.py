import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Corrección de estilos para evitar scroll excesivo
st.set_page_config(page_title="Ticket Pro IA", layout="wide")
st.markdown("<style>.stImage > img { max-height: 300px; width: auto; }</style>", unsafe_allow_html=True)

st.title("🏆 Parlay Maestro: Datos Reales")
engine = EVEngine()

archivo = st.file_uploader("Sube captura de Caliente/Liga MX", type=['png', 'jpg'])

if archivo:
    col_img, col_res = st.columns([1, 2])
    
    with col_img:
        st.image(archivo, caption="Captura Detectada") # Tamaño controlado

    with col_res:
        if st.button("🚀 Generar Parlay con Datos Reales"):
            with st.spinner("Buscando últimos 5 partidos en Google..."):
                # Llamada segura al lector de Cloud Vision
                try:
                    datos = analyze_betting_image(archivo)
                    todos, parlay = engine.analyze_matches(datos)
                    
                    if parlay:
                        st.success("🔥 MEJOR PARLAY SUGERIDO (Alta Probabilidad)")
                        for p in parlay:
                            st.info(f"✅ **{p['partido']}** | Pick: {p['pick']} ({p['confianza_texto']})")
                    
                    with st.expander("Ver análisis de Cascada completo"):
                        for j in todos:
                            st.write(f"🏟️ {j['partido']} - Goles HT: {j['goles_ht']}")
                except Exception as e:
                    st.error(f"Error técnico: {e}. Revisa tus credenciales de Google Cloud.")

