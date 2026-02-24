import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account

def analyze_betting_image(uploaded_file):
    # Carga credenciales directamente desde los secretos seguros
    creds_dict = st.secrets["google_credentials"]
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    client = vision.ImageAnnotatorClient(credentials=creds)
    
    content = uploaded_file.getvalue()
    image = vision.Image(content=content)
    
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if not texts: return {"juegos": []}

    full_text = texts[0].description
    lineas = [l.strip() for l in full_text.split('\n') if len(l.strip()) > 3]
    
    juegos_detectados = []
    # Lógica de emparejamiento mejorada para la captura de Caliente
    for i in range(0, len(lineas) - 1, 2):
        juegos_detectados.append({
            "home": lineas[i],
            "away": lineas[i+1],
            "momio": "+100" # Valor base si no se detecta
        })
            
    return {"juegos": juegos_detectados[:6]}
