import streamlit as st
from modules.ev_engine import EVEngine
# Asegúrate de que vision_reader esté importado correctamente

st.set_page_config(page_title="Ticket Pro IA", layout="wide")
engine = EVEngine()

st.title("🏟️ Ticket Pro IA: Análisis Dinámico")

# ... (Tu lógica de carga de archivo y analyze_betting_image)

if st.button("🚀 Iniciar Análisis Dinámico"):
    # resultado_ia = analyze_betting_image(archivo)
    picks = engine.analyze_matches(resultado_ia)
    
    for p in picks:
        # Recuperamos el diseño profesional de tarjetas
        with st.container(border=True):
            st.markdown(f"#### 🏟️ {p['partido']}")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.caption("Victoria")
                st.subheader(p['victoria']['pick'])
                st.write(f"🟢 {p['victoria']['prob']}")
                
            with col2:
                st.caption("Goles HT")
                st.subheader(p['goles_ht']['pick'])
                st.write(f"🟢 {p['goles_ht']['prob']}")
                
            with col3:
                st.caption("Ambos Anotan")
                st.subheader(p['btts']['pick'])
                st.write(f"🟢 {p['btts']['prob']}")
                
            with col4:
                st.caption("Tiros Esquina")
                st.subheader(p['corners']['pick'])
                st.write(f"🟢 {p['corners']['prob']}")
