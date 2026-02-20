import streamlit as st
import pandas as pd
import connector
import ev_engine # <--- Conectamos el motor estadístico

st.set_page_config(page_title="NBA ELITE v13", layout="wide")
st.title("🏀 NBA ELITE AI - ESCÁNER v13")

# --- LÓGICA DE CATEGORIZACIÓN (Tu esencia original) ---
def categorizar_pick(prob):
    if prob >= 0.65:
        return "🔥 EXCELENTE", "#00FF00" # Verde
    elif prob >= 0.58:
        return "⚡ BUENA", "#FFFF00"    # Amarillo
    else:
        return "⚠️ BAJA / EVITAR", "#FF4B4B" # Rojo

if st.button("🚀 EJECUTAR ANÁLISIS ESTADÍSTICO"):
    with st.spinner("Analizando promedios y momios de Caliente..."):
        datos_reales = connector.obtener_datos_caliente_limpios()
        
        resultados = []
        for p in datos_reales:
            # Calculamos probabilidad real con tu motor
            prob = ev_engine.calcular_probabilidad_over(p['home'], p['away'], p['linea'])
            status, color = categorizar_pick(prob)
            
            resultados.append({
                "PARTIDO": f"{p['away']} @ {p['home']}",
                "LÍNEA (OVER)": p['linea'],
                "PROB. IA": f"{prob*100:.1f}%",
                "STATUS": status,
                "COLOR": color,
                "INVERSIÓN": "2% Stake" if prob >= 0.58 else "0%"
            })
        
        df = pd.DataFrame(resultados)
        
        # --- RENDERIZADO VISUAL ---
        for _, row in df.iterrows():
            st.markdown(f"""
            <div style="border-left: 10px solid {row['COLOR']}; padding:15px; background-color:#1e1e1e; border-radius:5px; margin-bottom:10px">
                <h4 style="margin:0">{row['STATUS']} | {row['PARTIDO']}</h4>
                <p style="margin:0">Línea Sugerida: <b>{row['LÍNEA (OVER)']}</b> | Probabilidad: {row['PROB. IA']}</p>
                <p style="margin:0; font-size: 0.8em; color: gray;">Sugerencia: {row['INVERSIÓN']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.success("Análisis completado con datos de Caliente.")










