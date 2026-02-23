import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.connector import get_real_time_odds
from modules.ev_engine import calcular_ev  # Tu motor de EV

st.title("🎯 Ticket Pro IA: Análisis Exhaustivo +EV")

archivo = st.file_uploader("Sube captura de Caliente.mx", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, width=500)
    
    if st.button("🚀 Analizar Mercados", key="btn_analisis"):
        with st.spinner("🤖 Consultando Visión e IA..."):
            # 1. LA VARIABLE SE DEFINE AQUÍ
            datos_ia = analyze_betting_image(archivo)
            
            # 2. VALIDAMOS SI LA VARIABLE EXISTE Y TIENE DATOS
            if datos_ia and "juegos" in datos_ia:
                st.success(f"✅ Detectados {len(datos_ia['juegos'])} juegos")
                
                # 3. FILTRO EN CASCADA: Traemos datos reales de la API
                market_data = get_real_time_odds()
                
                for j in datos_ia["juegos"]:
                    with st.container(border=True):
                        # Extraemos el momio de la foto (Caliente)
                        momio_foto = int(j.get('moneyline', 0))
                        
                        # Simulación de Probabilidad para el motor de EV 
                        # (Aquí podrías conectar tus stats de jugadores)
                        prob_real = 0.55 # Ejemplo: 55% de probabilidad
                        
                        # 4. APLICAMOS TU MOTOR DE EV
                        valor_esperado = calcular_ev(prob_real, momio_foto)
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        col1.subheader(f"{j.get('away')} @ {j.get('home')}")
                        col2.metric("Momio Captura", momio_foto)
                        
                        # Color según el valor esperado
                        if valor_esperado > 0:
                            col3.metric("Valor (EV)", f"{valor_esperado*100}%", delta="Riesgo Óptimo")
                            st.info(f"🔥 Recomendación: El momio de {momio_foto} tiene valor matemático.")
                        else:
                            col3.metric("Valor (EV)", f"{valor_esperado*100}%", delta="Sin Valor", delta_color="inverse")
            else:
                st.error("La IA no pudo procesar los datos. Intenta con otra captura.")
