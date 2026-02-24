import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración de la página
st.set_page_config(
    page_title="Parlay Maestro IA", 
    page_icon="🎯", 
    layout="wide"
)

# Estilo personalizado para el título
st.title("🎯 Parlay Maestro: Análisis de Imagen")
st.markdown("---")

# 1. Verificación de Seguridad para evitar KeyError
if "GOOGLE_API_KEY" not in st.secrets or "google_credentials" not in st.secrets:
    st.error("⚠️ Error de configuración: Faltan llaves en los Secrets de Streamlit.")
    st.info("Asegúrate de haber añadido GOOGLE_API_KEY, GOOGLE_CSE_ID y google_credentials en el panel de Settings.")
    st.stop()

# 2. Interfaz de carga de imagen
st.sidebar.header("Configuración")
archivo = st.file_uploader("Sube tu captura de pantalla (Caliente / Liga MX)", type=['png', 'jpg', 'jpeg'])

if archivo:
    # Mostrar vista previa de la imagen cargada
    st.image(archivo, caption="Imagen cargada correctamente", width=500)
    
    # 3. Botón de ejecución
    if st.button("🚀 ANALIZAR PARTIDOS Y CALCULAR PROBABILIDAD"):
        with st.spinner("🤖 La IA está leyendo la imagen y analizando rachas recientes..."):
            try:
                # Paso A: Extraer equipos mediante Google Vision
                equipos_detectados = analyze_betting_image(archivo)
                
                if equipos_detectados and len(equipos_detectados) >= 2:
                    # Paso B: Inicializar motor de búsqueda y análisis
                    engine = EVEngine(
                        st.secrets["GOOGLE_API_KEY"], 
                        st.secrets["GOOGLE_CSE_ID"]
                    )
                    
                    # Paso C: Obtener análisis estadístico
                    todos_los_partidos, sugerencia_parlay = engine.analyze_matches(equipos_detectados)
                    
                    # 4. Visualización de Resultados (Semáforo)
                    st.subheader("📊 Resultados del Análisis")
                    
                    for p in todos_los_partidos:
                        prob = p['probabilidad']
                        
                        # Lógica de colores por probabilidad
                        if prob >= 75:
