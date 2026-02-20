import streamlit as st
import pandas as pd
import google.generativeai as genai
import sys
import os

# Añadimos el camino para importar tus otros módulos
sys.path.append(os.path.join(os.getcwd(), 'modules'))
import connector 

# --- CONFIGURACIÓN DE IA (GEMINI) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error al configurar la API Key de Gemini. Verifica tus Secrets.")

def obtener_analisis_ia(partido, jugador, linea, status):
    prompt = f"Analista NBA: El pick es {status}. Explica por qué el Over de {linea} para {jugador} en {partido} tiene valor técnico. Sé breve."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "IA analizando tendencias actuales..."

# --- LÓGICA DE ESCÁNER v3.0 ---
def evaluar_pick(prob_ia):
    prob_casa = 0.52 # Representa momio -110 de Caliente
    ventaja = prob_ia - prob_casa

    if ventaja > 0.08:
        return "🔥 SUGERENCIA ELITE", "green", 50
    elif ventaja > 0.03:
        return "⚡ BUENA", "blue", 20
    else:
        return "⚠️ Confianza insuficiente", "orange", 0

# --- INTERFAZ ---
st.set_page_config(page_title="NBA AI Scanner Pro", layout="wide")
st.title("🏀 NBA +EV Dashboard v12")

# --- CONEXIÓN REAL ---
st.sidebar.header("Configuración de Escáner")
if st.sidebar.button("🔄 Escanear Caliente.mx"):
    with st.spinner("Conectando con Caliente.mx y analizando con IA..."):
        # Aquí llamas a la función principal de tu connector.py
        # Suponiendo que devuelve una lista de diccionarios
        datos_reales = connector.obtener_datos_nba() 
        st.session_state['picks'] = pd.DataFrame(datos_reales)
        st.success("¡Datos actualizados!")

# Usamos datos en sesión para que no se borren al hacer clic
if 'picks' not in st.session_state:
    # Datos iniciales vacíos o de ejemplo hasta que des clic en Escanear
    st.info("Haz clic en 'Escanear Caliente.mx' para traer los partidos de hoy.")
else:
    df = st.session_state['picks']
    
    # Aplicar lógica de evaluación
    df[['status', 'color', 'stake']] = df.apply(lambda r: pd.Series(evaluar_pick(r['prob_modelo'])), axis=1)

    # --- MÉTRICAS ---
    picks_elite = df[df['status'] == "🔥 SUGERENCIA ELITE"]
    col1, col2 = st.columns(2)
    col1.metric("Oportunidades Elite", len(picks_elite))
    col2.metric("Partidos Escaneados", len(df))

    st.divider()

    # --- LISTADO DE TICKETS ---
    st.subheader("🕵️ Análisis de Mercado en Tiempo Real")
    
    for i, row in df.iterrows():
        # Filtramos para mostrar solo lo que tiene valor mínimo
        if row['stake'] > 0:
            with st.expander(f"{row['status']} | {row['game']}"):
                col_left, col_right = st.columns([2, 1])
                with col_left:
                    st.write(f"**Línea sugerida:** {row['linea']}")
                    st.write(f"**Probabilidad:** {row['prob_modelo']*100:.1f}%")
                    st.info(obtener_analisis_ia(row['game'], row['jugador'], row['linea'], row['status']))
                with col_right:
                    ticket = f"✅ *PRO PICK*\n🏀 {row['game']}\n🎯 {row['jugador']} Over {row['linea']}\n💰 Stake: {row['stake']} MXN"
                    st.code(ticket, language="text")
        else:
            # Mostrar los de confianza insuficiente de forma discreta
            st.write(f"❌ {row['game']} - {row['status']} (Prob: {row['prob_modelo']*100:.1f}%)")

st.divider()
st.subheader("📊 Historial de Sesión")
if 'picks' in st.session_state:
    st.dataframe(st.session_state['picks'], use_container_width=True)







