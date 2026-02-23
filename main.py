import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine  # Debe coincidir exactamente con la clase en ev_engine.py

# Inicializar motor (Asegúrate de que la clase se llame EVEngine con mayúsculas)
engine = EVEngine()

st.set_page_config(page_title="Ticket Pro IA", layout="wide")
st.title("🎯 Ticket Pro IA")

archivo = st.file_uploader("Sube captura", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, use_container_width=True)
    
    if st.button("🚀 Analizar Mercados", key="analizar_btn"):
        with st.spinner("🤖 Procesando imagen y calculando valor..."):
            # 1. Extraer datos con Visión IA
            resultado_ia = analyze_betting_image(archivo)
            
            # 2. Verificar que la IA devolvió datos válidos
            if resultado_ia and "juegos" in resultado_ia:
                # 3. Análisis con el motor de EV (Pasamos los datos de la IA)
                picks = engine.analyze_matches(resultado_ia)
                
                st.subheader("📊 Resultados del Análisis +EV")
                
                if picks:
                    for p in picks:
                        # Color y estilo dinámico según el valor
                        with st.container(border=True):
                            c1, c2, c3 = st.columns([2, 1, 1])
                            
                            with c1:
                                st.markdown(f"**{p['juego']}**")
                                st.caption(f"Status: {p['status']}")
                            
                            with c2:
                                st.metric("Momio Foto", p['momio'])
                            
                            with c3:
                                valor_pct = f"{round(p['ev'] * 100, 2)}%"
                                # Delta verde si el EV es positivo
                                st.metric("Valor (EV)", valor_pct, delta=p['status'], delta_color="normal")
                else:
                    st.info("No se encontraron oportunidades con valor positivo en esta captura.")
            else:
                st.error("La IA no pudo leer los mercados. Revisa la calidad de la imagen.")
