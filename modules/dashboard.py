import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests
import connector # Importación directa ya que están en la misma carpeta

# --- CONFIGURACIÓN DE IA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error al configurar Gemini.")

# --- FUNCIÓN TELEGRAM ---
def enviar_telegram(mensaje):
    try:
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensaje}&parse_mode=Markdown"
        requests.get(url)
    except Exception as e:
        st.warning(f"No se pudo enviar mensaje a Telegram: {e}")

def obtener_analisis_ia(partido, linea, status):
    prompt = f"Analista NBA: El pick es {status}. Explica brevemente por qué el Over de {linea} en {partido} es buena idea. Sé muy breve."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "IA analizando tendencias..."

# --- LÓGICA DE VALOR ---
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
st.set_page_config(page_title="NBA AI Dashboard", layout="wide")
st.title("🏀 NBA AI Dashboard + Telegram")

# Botón principal corregido
if st.button("🔄 Escanear y Notificar"):
    with st.spinner("Conectando con API y enviando alertas..."):
        # Usamos el nombre de función que sí funciona en tu prueba
        datos = connector.obtener_juegos() 
        df = pd.DataFrame(datos)
        
        for i, row in df.iterrows():
            status, color, stake = evaluar_pick(row['prob_modelo'])
            
            # Si es ELITE, mandamos a Telegram
            if status == "🔥 SUGERENCIA ELITE":
                analisis = obtener_analisis_ia(row['game'], row['linea'], status)
                msg = f"🚀 *PICK ELITE DETECTADO*\n\n🏀 {row['game']}\n🎯 Over {row['linea']}\n💰 Stake Sugerido: {stake} MXN\n\n🧠 *Análisis:* {analisis}"
                enviar_telegram(msg)
        
        st.session_state['picks_reales'] = df
        st.success("Escaneo completado y alertas enviadas.")

# Mostrar tabla de resultados si existen
if 'picks_reales' in st.session_state:
    st.subheader("📊 Partidos Detectados")
    st.dataframe(st.session_state['picks_reales'], use_container_width=True)







