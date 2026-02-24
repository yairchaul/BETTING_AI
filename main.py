import streamlit as st
# Vinculación directa con módulos
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Parlay Maestro", layout="wide")
st.title("🎯 Parlay Maestro: Sistema Sincronizado")

# Verificación de credenciales
if "google_credentials" not in st.secrets:
    st.error("❌ Configuración faltante en Secrets.")
    st.stop()

archivo = st.file_uploader("Sube tu captura", type=['png', 'jpg', 'jpeg'])

if archivo:
    if st.button("🚀 ANALIZAR AHORA"):
        # 1. Lectura
        equipos = analyze_betting_image(archivo)
        
        if equipos:
            # 2. Análisis (Vinculado a EVEngine)
            engine = EVEngine(st.secrets["GOOGLE_API_KEY"], st.secrets["GOOGLE_CSE_ID"])
            todos, parlay = engine.analyze_matches(equipos)
            
            # 3. Interfaz de Semáforo
            for p in todos:
                color = "#28a745" if p['probabilidad'] >= 75 else "#ffc107" if p['probabilidad'] >= 55 else "#dc3545"
                st.markdown(f"""
                    <div style="border-left: 5px solid {color}; padding: 10px; background: #1e1e1e; margin-bottom: 5px; border-radius: 5px;">
                        <b>{p['partido']}</b> | Pick: {p['pick']} ({p['probabilidad']}%)
                    </div>
                """, unsafe_allow_html=True)
            
            if parlay:
                st.success(f"✅ Sugerencia: Parlay de {len(parlay)} partidos listo.") # Error f-string corregido
        else:
            st.warning("No se detectaron equipos. Revisa la calidad de la imagen.")

