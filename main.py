import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración y Título
st.set_page_config(page_title="Parlay Maestro IA", layout="wide")
st.title("🎯 Parlay Maestro: Sistema Sincronizado")

# Verificación de Seguridad
if "google_credentials" not in st.secrets:
    st.error("❌ Error: No se detectaron las credenciales en Streamlit Secrets.")
    st.stop()

archivo = st.file_uploader("Sube tu captura de Caliente/Liga MX", type=['png', 'jpg', 'jpeg'])

if archivo:
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("🤖 Leyendo imagen y buscando estadísticas..."):
            # 1. Comunicación con Vision Reader
            equipos = analyze_betting_image(archivo)
            
            if equipos and len(equipos) >= 2:
                # 2. Comunicación con EV Engine
                engine = EVEngine(st.secrets["GOOGLE_API_KEY"], st.secrets["GOOGLE_CSE_ID"])
                todos, parlay = engine.analyze_matches(equipos)
                
                # 3. Renderizado del Semáforo Probabilístico
                st.subheader("📊 Resultados del Análisis")
                for p in todos:
                    prob = p['probabilidad']
                    # Asignación de colores por nivel de confianza
                    if prob >= 75:
                        color, emo = "#28a745", "🔥" # Verde
                    elif prob >= 55:
                        color, emo = "#ffc107", "⚖️" # Naranja
                    else:
                        color, emo = "#dc3545", "⚠️" # Rojo

                    st.markdown(f"""
                        <div style="border-left: 6px solid {color}; padding: 15px; background: #1e1e1e; margin-bottom: 10px; border-radius: 8px;">
                            <span style="font-size: 1.2em;">{emo} <b>{p['partido']}</b></span><br>
                            Sugerencia: <span style="color:{color}; font-weight:bold;">{p['pick']}</span> | 
                            Confianza: <b>{prob}%</b>
                        </div>
                    """, unsafe_allow_html=True)
                
                # 4. Resumen de Parlay Sugerido
                if parlay:
                    st.success(f"✅ Se recomienda un Parlay con {len(parlay)} partidos de alta confianza.")
            else:
                st.warning("⚠️ No se detectaron suficientes equipos en la imagen.")

