import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine, calcular_ev

# Inicializamos el motor de análisis
engine = EVEngine()

st.title("🎯 Betting AI: Analizador de Valor +EV")

archivo = st.file_uploader("Sube tu captura de Caliente", type=['png', 'jpg'])

if archivo:
    # 1. Visión: ¿Qué estoy viendo en Caliente?
    datos_ia = analyze_betting_image(archivo)
    
    if datos_ia:
        st.subheader("📊 Análisis de Probabilidad Real")
        
        for juego in datos_ia.get("juegos", []):
            # 2. Motor EV: Comparar momio de foto vs Probabilidad Estadística
            # Simulamos una probabilidad basada en el motor de Poisson del ev_engine
            prob_estatistica = 0.65  # Aquí el engine usará promedios reales
            momio_caliente = int(juego.get('moneyline', 100))
            
            ev = calcular_ev(prob_estatistica, momio_caliente)
            
            # 3. Visualización estilo "Parlay de Caliente"
            with st.expander(f"📌 {juego['away']} @ {juego['home']}", expanded=True):
                c1, c2 = st.columns(2)
                c1.metric("Momio Detectado", momio_caliente)
                
                # Resaltar si hay valor matemático (+EV)
                color = "normal" if ev > 0 else "inverse"
                c2.metric("Valor Esperado (EV)", f"{round(ev*100, 2)}%", delta=f"{round(ev,2)} pts", delta_color=color)

        # 4. El Objetivo: Sugerir el mejor Parlay posible
        if st.button("🏆 Generar Parlay Sugerido"):
            # Aquí el engine filtra por el threshold del 70% que definiste
            picks, parlay = engine.analyze_matches() 
            st.write("Basado en el análisis, este es el parlay con mayor ventaja sobre la casa:")
            st.json(picks)
