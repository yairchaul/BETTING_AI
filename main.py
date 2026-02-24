import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Parlay Maestro IA", layout="wide")
st.title("🎯 Parlay Maestro: Análisis de Imagen")

# Verificación de que las llaves existen en el panel de Settings
if "google_credentials" not in st.secrets:
    st.error("Faltan las credenciales en los Secrets de Streamlit.")
    st.stop()

archivo = st.file_uploader("Sube tu captura de Caliente", type=['png', 'jpg', 'jpeg'])

if archivo:
    if st.button("🚀 ANALIZAR PARTIDOS"):
        with st.spinner("🤖 Analizando racha de los últimos partidos..."):
            equipos = analyze_betting_image(archivo)
            
            if equipos:
                engine = EVEngine(st.secrets["GOOGLE_API_KEY"], st.secrets["GOOGLE_CSE_ID"])
                todos, parlay = engine.analyze_matches(equipos)
                
                st.subheader("📊 Probabilidades Detectadas")
                for p in todos:
                    prob = p['probabilidad']
                    # Lógica de semáforo solicitada
                    if prob >= 75: color, emo = "#28a745", "🔥" # Verde (Alta)
                    elif prob >= 55: color, emo = "#ffc107", "⚖️" # Naranja (Media)
                    else: color, emo = "#dc3545", "⚠️" # Rojo (Baja)
                    
                    st.markdown(f"""
                        <div style="border-left: 5px solid {color}; padding: 15px; margin-bottom: 10px; background-color: #1e1e1e; border-radius: 5px;">
                            <span style="font-size: 20px;">{emo}</span> 
                            <b>{p['partido']}</b> | Pick: <span style="color:{color};">{p['pick']}</span> 
                            <br><small>Confianza del análisis: {prob}%</small>
                        </div>
                    """, unsafe_allow_html=True)
                
                if parlay:
                    st.success(f"✅ Se recomienda un Parlay de {len(parlay)} partidos.")
            else:
                st.warning("No se detectaron equipos. Asegúrate de que la imagen sea clara.")

if archivo:
    # Mostramos la imagen para confirmar que se cargó bien
    st.image(archivo, caption="Captura cargada", use_container_width=True)
    
    if st.button("🚀 ANALIZAR PARTIDOS"):
        # Importante: resetear el puntero del archivo para que Vision pueda leerlo desde el inicio
        archivo.seek(0) 
        
        with st.spinner("🤖 Leyendo imagen..."):
            equipos = analyze_betting_image(archivo)
            
            if equipos and len(equipos) > 0:
                # ... resto del código del motor de análisis ...
                st.success(f"Detectadas {len(equipos)} líneas de texto.")
            else:
                st.error("No se pudo extraer texto. Revisa que la imagen no esté borrosa.")
