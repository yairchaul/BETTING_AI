import requests
from config import TELEGRAM_TOKEN, CHAT_ID

def enviar_pick:

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url,data={
        "chat_id":939085593,
        "text":msg

    })
