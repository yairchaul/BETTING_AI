import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Inicializar motor
engine = EVEngine()

st.title("🎯 Ticket Pro IA")

archivo = st.file_uploader("Sube captura", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, use_container_width=True)
    
    if st.button("🚀 Analizar Mercados", key="analizar_btn"):
        with st.spinner("🤖 Calculando EV..."):
            # 1. Extraer datos con Visión IA
            resultado_ia = analyze_betting_image(archivo)
            
            # 2. Verificar que la IA devolvió datos válidos
            if resultado_ia and "juegos" in resultado_ia:
                # 3. Análisis exhaustivo con el motor de EV
                picks = engine.analyze_matches(resultado_ia)
                
                st.subheader("📊 Resultados del Análisis +EV")
                
                for p in picks:
                    # Color según el valor esperado
                    color = "green" if p['ev'] > 0.05 else "white"
                    
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.markdown(f"**{p['juego']}**")
                        c1.caption(f"Status: {p['status']}")
                        
                        c2.metric("Momio", p['momio'])
                        
                        # Resaltar en verde si hay mucha ventaja
                        valor_texto = f"{round(p['ev'] * 100, 2)}%"
                        c3.metric("Valor (EV)", valor_texto, delta=p['status'], delta_color="normal")
            else:
                st.error("La IA no pudo leer los mercados. Intenta con una captura más clara.")
