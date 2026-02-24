import streamlit as st
from google.oauth2 import service_account
from google.cloud import vision
import io

def get_vision_client():
    try:
        # Creamos una copia para no dañar los secretos originales en memoria
        creds_info = dict(st.secrets["google_credentials"])
        # Corregimos el formato de la llave PEM
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
        
        credentials = service_account.Credentials.from_service_account_info(creds_info)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"Error de autenticación: {e}")
        return None

def analyze_betting_image(image_file):
    client = get_vision_client()
    if not client: return []

    content = image_file.read()
    image = vision.Image(content=content)
    
    # Detectar texto en la imagen
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if not texts:
        return []

    # Lógica simplificada para extraer equipos (primeras líneas detectadas)
    # Aquí puedes mejorar el filtrado según el formato de Caliente
    lineas = texts[0].description.split('\n')
    return [linea.strip() for linea in lineas if len(linea) > 3][:10]
