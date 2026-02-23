import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# 1. Configuración de página y estilos compactos
st.set_page_config(page_title="Ticket Pro IA", layout="wide")

st.markdown("""
    <style>
    /* Reducir espacio superior */
    .block-container { padding-top: 1rem; }
    /* Hacer métricas más pequeñas */
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    /* Ajustar cabeceras de tarjetas */
    .stMarkdown h4 { margin-bottom: -15px; font-size: 0.9rem !important; }
    </style>
""", unsafe_allow_html=True)

engine = EVEngine()

st.title("🎯 Ticket Pro IA: Análisis Fútbol")

# 2. Área de carga de archivo
archivo = st.file_uploader("Sube tu captura de Caliente/Liga MX", type=['png', 'jpg', 'jpeg'])

if archivo:
    # DISEÑO DE COLUMNAS: Imagen a la izquierda, Controles a la derecha
    col_img, col_ctrl = st.columns([1, 2])
    
    with col_img:
        # Imagen con tamaño fijo para que no desplace hacia abajo
        st.image(archivo, caption="Captura", width=280)
    
    with col_ctrl:
        st.success("✅ Imagen cargada")
        ejecutar = st.button("🚀 Iniciar Análisis en Cascada", use_container_width=True)

    # 3. Organización por Pestañas para ahorrar espacio vertical
    if ejecutar:
        with st.spinner("🤖 Analizando capas de probabilidad..."):
            resultado_ia = analyze_betting_image(archivo)
            
            if resultado_ia and "juegos" in resultado_ia:
                picks = engine.analyze_matches(resultado_ia)
                
                tab_analisis, tab_resumen = st.tabs(["📊 Análisis Detallado", "📝 Resumen Social"])
                
                with tab_analisis:
                    # Mostrar tarjetas en formato compacto
                    for p in picks:
                        with st.container(border=True):
                            st.markdown(f"#### 🏟️ {p['partido']} | Momio: `{p['momio']}`")
                            # 4 Columnas internas para las capas
