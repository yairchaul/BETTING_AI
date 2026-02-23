# telegram_bot.py
import requests
from config import TELEGRAM_TOKEN, CHAT_ID

def enviar_pick(msg): # CORREGIDO: Se añadieron paréntesis y el argumento 'msg'
    """
    Envía el pick analizado al chat de Telegram configurado.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        response = requests.post(url, data={
            "chat_id": 939085593, # ID de chat directo
            "text": msg
        })
        return response.json()
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")
        return None
