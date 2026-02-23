# app.py
import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import calcular_ev

st.title("🏀 Ticket Pro - Vision Terminal")

# Sidebar: Gestión de Bankroll
bankroll = st.sidebar.number_input("Bankroll actual (MXN)", value=1000.0)

# Carga de Imagen
st.header("📸 Scanner de Mercados")
archivo = st.file_uploader("Sube captura de Caliente.mx", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, caption="Captura subida", use_column_width=True)
    
    if st.button("🔥 Analizar con IA"):
        with st.spinner("IA leyendo mercados..."):
            datos = analyze_betting_image(archivo)
            
            if datos and "juegos" in datos:
                st.success("Mercados extraídos con éxito")
                for juego in datos["juegos"]:
                    with st.expander(f"📌 {juego['away']} @ {juego['home']}"):
                        col1, col2 = st.columns(2)
                        col1.write(f"Línea Total: {juego['total_line']}")
                        col1.write(f"Momio Over: {juego['odds_over']}")
                        
                        # Aquí conectaríamos el EV Engine
                        ev = calcular_ev(0.55) # Probabilidad ejemplo
                        st.metric("Expected Value", f"{ev*100:.2f}%")
            else:
                st.error("No se pudieron extraer datos. Intenta con una imagen más clara.")
