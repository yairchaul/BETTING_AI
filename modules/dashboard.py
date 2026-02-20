import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests
# Importamos tu conector local
import connector # Como ambos están en la misma carpeta, se importan directo

# --- CONFIGURACIÓN DE APIS ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error en API Key de Gemini.")

def enviar_telegram(mensaje):
    token = st.secrets["TELEGRAM_BOT_TOKEN"]
    chat_id = st.secrets["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensaje}&parse_mode=Markdown"
    requests.get(url)

def obtener_analisis_ia(partido, jugador, linea, status):
    prompt = f"Analista NBA: El pick es {status}. Explica por qué el Over de {linea} para {jugador} en {partido} es buena apuesta. Sé breve."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "IA analizando tendencias..."

# --- LÓGICA DE ESCÁNER v3.0 ---
def evaluar_pick(prob_ia):
    prob_casa = 0.52 
    ventaja = prob_ia - prob_casa
    if ventaja > 0.08:
        return "🔥 SUGERENCIA ELITE", "green", 50
    elif ventaja > 0.03:
        return "⚡ BUENA", "blue", 20
    else:
        return "⚠️ Confianza insuficiente", "orange", 0

# --- INTERFAZ ---
st.set_page_config(page_title="NBA AI Pro", layout="wide")
st.title("🏀 NBA AI Dashboard + Telegram")

if st.button("🔄 Escanear y Notificar"):
    with st.spinner("Escaneando Caliente.mx..."):
        # Llamamos a tu función de connector.py
        # NOTA: Debes editar connector.py para que use st.secrets["ODDS_API_KEY"]
        datos = connector.obtener_datos_reales() 
        df = pd.DataFrame(datos)
        
        for i, row in df.iterrows():
            status, color, stake = evaluar_pick(row['prob_modelo'])
            if status == "🔥 SUGERENCIA ELITE":
                analisis = obtener_analisis_ia(row['game'], row['jugador'], row['linea'], status)
                msg = f"🚀 *NUEVA SUGERENCIA ELITE*\n\n🏀 {row['game']}\n🎯 {row['jugador']} Over {row['linea']}\n💰 Stake: {stake} MXN\n\n🧠 *Análisis IA:* {analisis}"
                enviar_telegram(msg)
                st.success(f"Notificación enviada: {row['game']}")
        
        st.session_state['picks'] = df

# Mostrar resultados
if 'picks' in st.session_state:
    st.dataframe(st.session_state['picks'], use_container_width=True)







