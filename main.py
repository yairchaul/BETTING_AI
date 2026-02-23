import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine, calcular_ev

# Inicializamos el motor
engine = EVEngine()

st.title("🎯 Ticket Pro IA: Analizador +EV")

archivo = st.file_uploader("Sube captura de Caliente.mx", type=['png', 'jpg', 'jpeg'])

if archivo:
    # Mostrar la imagen que el usuario subió
    st.image(archivo, caption="Captura cargada", use_container_width=True)
    
    if st.button("🚀 Analizar Mercados"):
        with st.spinner("🤖 Procesando visión y cálculos de valor..."):
            # 1. Visión IA: Extraer datos de la imagen
            datos_ia = analyze_betting_image(archivo)
            
            if datos_ia and "juegos" in datos_ia:
                st.success(f"✅ Detectados {len(datos_ia['juegos'])} mercados")
                
                # 2. Análisis de Valor: Pasamos los datos al motor de EV
                picks = engine.analyze_matches(datos_ia)
                
                # 3. Visualización Exhaustiva
                for p in picks:
                    # Determinamos el color según el valor (EV)
                    es_alto_valor = p['status'] == "🔥 TOP VALUE"
                    color_borde = "green" if es_alto_valor else "gray"
                    
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{p['juego']}**")
                            st.caption(f"Status: {p['status']}")
                        
                        with col2:
                            st.metric("Momio Foto", f"{p['momio']}")
                        
                        with col3:
                            # Mostramos el EV como porcentaje
                            st.metric("Valor (EV)", f"{round(p['ev'] * 100, 1)}%", 
                                      delta="VENTAJA" if p['ev'] > 0 else "RIESGO")

                if not picks:
                    st.warning("⚠️ No se encontraron apuestas con valor positivo en esta captura.")
            else:
                st.error("La IA no pudo extraer datos válidos. Revisa la calidad de la imagen.")
