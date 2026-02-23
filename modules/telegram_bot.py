# modules/telegram_bot.py
import requests
import streamlit as st

def enviar_pick(msg):
    """
    Envía el pick usando los Secrets de Streamlit.
    """
    try:
        # Lee directamente de los Secrets de la nube
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["CHAT_ID"]
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        response = requests.post(url, data={
            "chat_id": chat_id,
            "text": msg
        })
        return response.json()
    except Exception as e:
        st.error(f"Error de configuración de Telegram: {e}")
        return None
