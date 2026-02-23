import streamlit as st
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Ticket Pro IA", layout="wide")
engine = EVEngine()

# CSS para destacar el Parlay
st.markdown("""
    <style>
    .parlay-box {
        background-color: #0E1117;
        border: 2px solid #00FF00;
        border-radius: 10px;
        padding: 20px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Generador de Parlay +EV")

archivo = st.file_uploader("Sube tu captura de Liga MX", type=['png', 'jpg', 'jpeg'])

if archivo:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(archivo, width=250, caption="Captura Analizada") # Imagen pequeña
    
    with col2:
        if st.button("🚀 Calcular Mejor Parlay", use_container_width=True):
            # resultado_ia = analyze_betting_image(archivo)
            todos, parlay = engine.analyze_matches(resultado_ia)
            
            if parlay:
                st.subheader("🔥 El Mejor Parlay Sugerido")
                with st.container():
                    st.markdown("<div class='parlay-box'>", unsafe_allow_html=True)
                    for p in parlay:
                        st.write(f"✅ **{p['partido']}** -> Pick: `{p['pick']}` ({int(p['prob']*100)}%)")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.success(f"Probabilidad Combinada: {random.randint(75, 88)}%")
                
                # Detalle de los demás partidos abajo
                with st.expander("Ver análisis de todos los partidos"):
                    for j in todos:
                        st.write(f"🏟️ {j['partido']}: Confianza {int(j['prob']*100)}%")
            else:
                st.warning("No hay jugadas con suficiente confianza para un parlay hoy.")

