import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Parlay Maestro IA", layout="wide")

st.title("🎯 Parlay Maestro: Análisis de Imagen")

# Verificación de Secrets
if "google_credentials" not in st.secrets:
    st.error("⚠️ Configura 'google_credentials' en los Secrets de Streamlit.")
    st.stop()

archivo = st.file_uploader("Sube tu captura de Caliente", type=['png', 'jpg', 'jpeg'])

if archivo:
    if st.button("🚀 ANALIZAR PARTIDOS"):
        with st.spinner("🤖 Procesando imagen y analizando rachas actuales..."):
            # 1. Visión
            equipos = analyze_betting_image(archivo)
            
            if equipos:
                # 2. Análisis Estadístico
                engine = EVEngine(st.secrets["GOOGLE_API_KEY"], st.secrets["GOOGLE_CSE_ID"])
                todos, parlay = engine.analyze_matches(equipos)
                
                st.subheader("📊 Análisis por Partido")
                for p in todos:
                    prob = p['probabilidad']
                    # Semáforo de colores
                    if prob >= 75: color, emo = "#28a745", "🔥" # Verde
                    elif prob >= 55: color, emo = "#ffc107", "⚖️" # Naranja
                    else: color, emo = "#dc3545", "⚠️" # Rojo
                    
                    st.markdown(f"""
                        <div style="border-left: 5px solid {color}; padding: 15px; margin-bottom: 10px; background-color: #1e1e1e; border-radius: 5px;">
                            <span style="font-size: 20px;">{emo}</span> 
                            <b>{p['partido']}</b> | Pick: <span style="color:{color};">{p['pick']}</span> 
                            <br><small>Confianza: {prob}%</small>
                        </div>
                    """, unsafe_allow_html=True)
                
                if parlay:
                    st.success(f"🔥 Sugerencia de Parlay: {len(parlay)} partidos seleccionados.")
            else:
                st.warning("No se detectaron equipos. Intenta con una imagen más clara.")
