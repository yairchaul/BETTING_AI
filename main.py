import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración inicial de la página
st.set_page_config(page_title="Parlay Maestro IA", page_icon="🎯", layout="wide")

st.title("🎯 Parlay Maestro: Análisis de Imagen")
st.markdown("---")

# 1. Verificación de Secrets para evitar errores de llave faltante
if "google_credentials" not in st.secrets or "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Configuración incompleta: Faltan las llaves en los Secrets de Streamlit.")
    st.info("Asegúrate de haber pegado el bloque [google_credentials] y las llaves API en Settings.")
    st.stop()

# 2. Interfaz de carga
archivo = st.file_uploader("Sube tu captura de pantalla (Caliente / Liga MX)", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, caption="Imagen cargada correctamente", width=400)
    
    if st.button("🚀 ANALIZAR PARTIDOS"):
        with st.spinner("🤖 Procesando imagen y analizando probabilidades..."):
            try:
                # Paso A: Extraer texto de la imagen
                equipos = analyze_betting_image(archivo)
                
                if equipos and len(equipos) > 0:
                    # Paso B: Inicializar motor de análisis
                    engine = EVEngine(
                        st.secrets["GOOGLE_API_KEY"], 
                        st.secrets["GOOGLE_CSE_ID"]
                    )
                    
                    todos, parlay = engine.analyze_matches(equipos)
                    
                    # 3. Visualización con Semáforo (Aquí estaba el error de indentación)
                    st.subheader("📊 Análisis Probabilístico")
                    
                    for p in todos:
                        prob = p.get('probabilidad', 50)
                        
                        # Definición de colores y emojis según confianza
                        if prob >= 75:
                            color, emoji = "#28a745", "🔥" # Verde (Alta)
                        elif prob >= 55:
                            color, emoji = "#ffc107", "⚖️" # Naranja (Media)
                        else:
                            color, emoji = "#dc3545", "⚠️" # Rojo (Baja)
                        
                        # Cuadro de resultado visual
                        st.markdown(f"""
                            <div style="border-left: 5px solid {color}; padding: 15px; margin-bottom: 10px; background-color: #1e1e1e; border-radius: 5px;">
                                <span style="font-size: 20px;">{emoji}</span> 
                                <b>{p['partido']}</b> | Pick: <span style="color:{color}; font-weight:bold;">{p['pick']}</span> 
                                <br><small>Confianza: {prob}%</small>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    if parlay:
                        st.success(f"✅ Se recomienda un Parl

