import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración de página
st.set_page_config(page_title="Ticket Pro IA - Fútbol", layout="wide")

# Inicializar motor
engine = EVEngine()

st.title("🎯 Analizador de Cascada Fútbol")
st.markdown("### Sube tu captura de Caliente para análisis exhaustivo")

archivo = st.file_uploader("Arrastra tu imagen aquí", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, caption="Captura Detectada", use_container_width=True)
    
    if st.button("🚀 Iniciar Análisis en Cascada", use_container_width=True):
        with st.spinner("🤖 IA analizando capas de probabilidad..."):
            # 1. Visión IA (Asegúrate que use gemini-1.5-flash)
            resultado_ia = analyze_betting_image(archivo)
            
            if resultado_ia and "juegos" in resultado_ia:
                st.success(f"✅ Se detectaron {len(resultado_ia['juegos'])} encuentros.")
                
                # 2. Ejecutar Motor de Cascada
                analisis_final = engine.analyze_matches(resultado_ia)
                
                # 3. Mostrar Resultados (Estilo Tarjeta Parlay)
                for p in analisis_final:
                    with st.container(border=True):
                        st.subheader(f"⚽ {p['partido']}")
                        st.caption(f"Momio detectado: {p['momio_origen']}")
                        
                        # Columnas para las 4 capas de cascada
                        cols = st.columns(4)
                        for i, capa in enumerate(p['capas']):
                            with cols[i]:
                                st.write(f"**{capa['nivel']}**")
                                st.write(capa['detalle'])
                                st.metric(label="Confianza", value=capa['valor'], delta=capa['status'])
                
                st.info("💡 Consejo: Selecciona los niveles con 'Confianza ALTA' para tu parlay.")
            else:
                st.error("No se pudieron extraer datos. Verifica que los nombres de los equipos sean visibles.")
