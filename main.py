import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Parlay Maestro", layout="wide")

# Título visible siempre para saber que la app cargó
st.title("🎯 Parlay Maestro: Análisis de Imagen")

# Verificación de llaves para evitar que la app muera en silencio
if "GOOGLE_CSE_ID" not in st.secrets:
    st.error("Faltan las llaves en los Secrets de Streamlit.")
    st.stop()

# Subida de imagen
archivo = st.file_uploader("Sube la captura de tus partidos (Caliente/Liga MX)", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, caption="Imagen cargada correctamente", width=400)
    
    if st.button("🚀 ANALIZAR PARTIDOS Y DAR OPCIONES"):
        with st.spinner("Procesando imagen y buscando datos reales..."):
            try:
                # 1. Leer texto de la imagen (Equipos y Momios)
                datos_imagen = analyze_betting_image(archivo)
                
                # 2. El motor busca rachas y genera las opciones
                engine = EVEngine(st.secrets["GEMINI_API_KEY"], st.secrets["GOOGLE_CSE_ID"])
                opciones, mejor_parlay = engine.analyze_matches(datos_imagen)
                
                # 3. Mostrar resultados
                if mejor_parlay:
                    st.success("✅ Opciones de análisis listas")
                    for p in mejor_parlay:
                        st.write(f"🔹 **{p['partido']}** -> Pick Sugerido: {p['pick']}")
            except Exception as e:
                st.error(f"Hubo un problema al procesar la imagen: {e}")
