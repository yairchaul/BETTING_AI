import streamlit as st
import pandas as pd
import tracker # Asegúrate de tener el tracker.py que configuramos antes

# --- BARRA LATERAL: GESTIÓN DE DINERO ---
with st.sidebar:
    st.header("💰 Gestión de Capital")
    capital_total = st.number_input("Ingresa tu monto disponible (MXN):", value=1000.0, step=100.0)
    
    tipo_apuesta = st.radio(
        "Estrategia de Inversión:",
        ["Independiente (Fija)", "En Cadena (Progresiva)"],
        help="Independiente usa un % fijo. En Cadena ajusta el monto según el éxito previo."
    )
    
    riesgo = st.select_slider(
        "Nivel de Riesgo:",
        options=["Conservador", "Moderado", "Agresivo"],
        value="Moderado"
    )

# --- LÓGICA DE CÁLCULO DE STAKE ---
def calcular_monto_a_invertir(capital, probabilidad, riesgo_nivel):
    # Porcentajes de Stake sugeridos según nivel
    dict_riesgo = {"Conservador": 0.01, "Moderado": 0.02, "Agresivo": 0.05}
    base_stake = dict_riesgo[riesgo_nivel]
    
    # Si la probabilidad es EXCELENTE (>70%), aumentamos un poco el stake
    if probabilidad > 0.70:
        return capital * (base_stake * 1.5)
    return capital * base_stake
    if st.button("🚀 ESCANEAR Y CALCULAR APUESTAS"):
    datos_api = connector.obtener_datos_caliente_limpios()
    
    st.subheader(f"🎯 Plan de Inversión para ${capital_total} MXN")
    
    for p in datos_api:
        prob = ev_engine.calcular_probabilidad_over(p['home'], p['away'], p['linea'])
        
        # Solo operamos con picks BUENOS o EXCELENTES
        if prob >= 0.58:
            monto_sugerido = calcular_monto_a_invertir(capital_total, prob, riesgo)
            status = "🔥 EXCELENTE" if prob >= 0.70 else "⚡ BUENA"
            
            # Visualización en pantalla
            st.warning(f"**{status}**: {p['away']} @ {p['home']} | Over {p['linea']}")
            st.write(f"👉 Invertir: **${monto_sugerido:.2f} MXN** (Basado en estrategia {tipo_apuesta})")
            
            # REGISTRO EN EL TRACKER
            tracker.registrar_apuesta(
                partido=f"{p['away']}@{p['home']}",
                jugador="Total Puntos",
                linea=p['linea'],
                prob=prob,
                stake=monto_sugerido,
                status=status
            )
            
            # Si es 'En Cadena', el capital para la siguiente apuesta se ajusta (simulado)
            if tipo_apuesta == "En Cadena (Progresiva)":
                capital_total += (monto_sugerido * 0.90) # Asumimos ganancia para el siguiente cálculo









