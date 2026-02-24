import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración de página
st.set_page_config(page_title="Parlay Maestro IA", layout="wide")
st.title("🎯 Parlay Maestro: Análisis en Tiempo Real")

# 1. Validación de Secretos
if "google_credentials" not in st.secrets:
    st.error("❌ No se detectaron las credenciales en Streamlit Cloud.")
    st.stop()

# 2. Carga de imagen
archivo = st.file_uploader("Sube la captura de tus momios", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, caption="Captura cargada", width=400)
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("🤖 Leyendo equipos y calculando probabilidades..."):
            # A. Obtener equipos desde Vision
            equipos = analyze_betting_image(archivo)
            
            if equipos and len(equipos) >= 2:
                # B. Ejecutar Motor de Análisis
                engine = EVEngine(
                    st.secrets["GOOGLE_API_KEY"], 
                    st.secrets["GOOGLE_CSE_ID"]
                )
                todos, parlay = engine.analyze_matches(equipos)
                
                # C. Visualización de Semáforo
                st.subheader("📊 Resultados del Análisis")
                for p in todos:
                    prob = p['probabilidad']
                    # Lógica de colores
                    if prob >= 75: color, emo = "#28a745", "🔥" # Verde
                    elif prob >= 55: color, emo = "#ffc107", "⚖️" # Naranja
                    else: color, emo = "#dc3545", "⚠️" # Rojo
                    
                    st.markdown(f"""
                        <div style="border-left: 6px solid {color}; padding: 15px; background: #1e1e1e; margin-bottom: 10px; border-radius: 8px;">
                            <span style="font-size: 1.1em;">{emo} <b>{p['partido']}</b></span><br>
                            Sugerencia: <span style="color:{color}; font-weight:bold;">{p['pick']}</span> | 
                            Confianza: <b>{prob}%</b>
                        </div>
                    """, unsafe_allow_html=True)
                
                # D. Resumen de Parlay Sugerido
                if parlay:
                    st.success(f"✅ Se recomienda un Parlay con {len(parlay)} partidos seleccionados.")
            else:
                st.warning("⚠️ No se detectaron equipos suficientes. Verifica que la imagen sea nítida.")


