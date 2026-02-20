import streamlit as st
import pandas as pd
import google.generativeai as genai
import connector 

# --- CONFIGURACIÓN DE IA ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- LÓGICA DE VALOR V3.0 (Recuperando la esencia) ---
def evaluar_pick(prob_ia):
    # La casa suele ofrecer 52.4% en momio -110
    prob_casa = 0.52 
    ventaja = prob_ia - prob_casa
    
    if ventaja > 0.10:
        return "🔥 SUGERENCIA ELITE", "#00FF00", "EXCELENTE" # Verde brillante
    elif ventaja > 0.05:
        return "⚡ BUENA", "#FFFF00", "RECOMENDADA"      # Amarillo
    else:
        return "⚠️ Confianza insuficiente", "#FFA500", "EVITAR" # Naranja

# --- INTERFAZ ---
st.set_page_config(page_title="NBA ELITE SCANNER", layout="wide")
st.title("🏀 NBA ELITE AI - SISTEMA DE VALOR v13")

# --- GESTIÓN DE CAPITAL ---
with st.sidebar:
    st.header("💰 Gestión de Bankroll")
    capital_inicial = st.number_input("Tu Capital Actual (MXN):", value=1000.0)
    st.info(f"Capital para invertir: ${capital_inicial}")

# --- ESCÁNER Y PROCESAMIENTO ---
if st.button("🔄 EJECUTAR ESCÁNER DE VALOR"):
    with st.spinner("Buscando ventajas en Caliente.mx..."):
        # Traemos los juegos reales que ya logramos conectar
        datos_api = connector.obtener_juegos()
        
        # Simulamos la integración con tu ev_engine para nombres de jugadores
        # En el futuro, tu connector extraerá 'player_totals' de la API
        for p in datos_api:
            status, color, nivel = evaluar_pick(p['prob_modelo'])
            p['STATUS'] = status
            p['COLOR'] = color
            p['NIVEL'] = nivel
            # Calculamos ganancia potencial basada en momio y stake (2% del bankroll)
            p['STAKE_MXN'] = capital_inicial * 0.02 if nivel != "EVITAR" else 0
            p['PROB_REAL'] = f"{p['prob_modelo']*100}%"
        
        st.session_state['picks_v13'] = pd.DataFrame(datos_api)

# --- VISUALIZACIÓN DE INVERSIÓN ---
if 'picks_v13' in st.session_state:
    df = st.session_state['picks_v13']
    
    st.subheader("🎯 Oportunidades de Inversión Detectadas")
    
    # Creamos las "Tarjetas de Apuesta" con la esencia original
    for i, row in df.iterrows():
        if row['NIVEL'] != "EVITAR":
            # Usamos el color verde para las ELITE como pediste
            st.markdown(f"""
            <div style="border: 2px solid {row['COLOR']}; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: #1e1e1e;">
                <h3 style="color: {row['COLOR']}; margin: 0;">{row['STATUS']} - Confianza {row['NIVEL']}</h3>
                <p style="margin: 5px 0;"><b>Partido:</b> {row['game']} | <b>Línea:</b> Over {row['linea']}</p>
                <p style="margin: 5px 0;"><b>Inversión Sugerida:</b> ${row['STAKE_MXN']:.2f} MXN | <b>Probabilidad IA:</b> {row['PROB_REAL']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Registro y Control de Datos")
    st.dataframe(df[['game', 'STATUS', 'linea', 'PROB_REAL', 'STAKE_MXN']], use_container_width=True)








