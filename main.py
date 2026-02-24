import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración inicial
st.set_page_config(page_title="Parlay Maestro IA", page_icon="🎯", layout="wide")

st.title("🎯 Parlay Maestro: Análisis de Imagen")
st.markdown("---")

# 1. Verificación de Seguridad para evitar KeyError
if "google_credentials" not in st.secrets or "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Faltan llaves en los Secrets de Streamlit.")
    st.stop()

# 2. Interfaz de carga
archivo = st.file_uploader("Sube tu captura de pantalla (Caliente / Liga MX)", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, caption="Imagen cargada", width=400)
    
    if st.button("🚀 ANALIZAR PARTIDOS"):
        with st.spinner("🤖 Analizando probabilidades..."):
            try:
                # Paso A: Procesar imagen
                equipos = analyze_betting_image(archivo)
                
                if equipos and len(equipos) >= 2:
                    # Paso B: Motor de análisis
                    engine = EVEngine(
                        st.secrets["GOOGLE_API_KEY"], 
                        st.secrets["GOOGLE_CSE_ID"]
                    )
                    
                    todos, parlay = engine.analyze_matches(equipos)
                    
                    # 3. Visualización con Semáforo
                    st.subheader("📊 Resultados del Análisis")
                    
                    for p in todos:
                        prob = p.get('probabilidad', 50)
                        
                        if prob >= 75:
                            color, emoji = "#28a745", "🔥" # Verde
                        elif prob >= 55:
                            color, emoji = "#ffc107", "⚖️" # Naranja
                        else:
                            color, emoji = "#dc3545", "⚠️" # Rojo
                        
                        st.markdown(f"""
                            <div style="border-left: 5px solid {color}; padding: 15px; margin-bottom: 10px; background-color: #1e1e1e; border-radius: 5px;">
                                <span style="font-size: 20px;">{emoji}</span> 
                                <b>{p['partido']}</b> | Pick: <span style="color:{color}; font-weight:bold;">{p['pick']}</span> 
                                <br><small>Confianza: {prob}%</small>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Corrección del error de cierre de f-string
                    if parlay:
                        st.success(f"✅ Se recomienda un Parlay con {len(parlay)} partidos seleccionados.")
                else:
                    st.warning("No se detectaron suficientes equipos en la imagen.")
                    
            except Exception as e:
                st.error(f"Error al procesar: {e}")
else:
    st.info("Sube una imagen para comenzar.")

