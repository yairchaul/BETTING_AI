import streamlit as st
from google.oauth2 import service_account
from google.cloud import vision
import io

def get_vision_client():
    try:
        # Extraemos las credenciales
        creds_info = dict(st.secrets["google_credentials"])
        
        # Limpieza profunda de la llave para evitar el error de longitud (PEM)
        pk = creds_info["private_key"].replace("\\n", "\n").strip()
        creds_info["private_key"] = pk
        
        credentials = service_account.Credentials.from_service_account_info(creds_info)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"Error técnico en Vision: {e}")
        return None

def analyze_betting_image(image_file):
    client = get_vision_client()
    if not client: return []

    # Resetear el puntero de la imagen
    image_file.seek(0)
    content = image_file.read()
    image = vision.Image(content=content)
    
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if not texts: return []

    # Extraer texto y limpiar
    lineas = texts[0].description.split('\n')
    return [l.strip() for l in lineas if len(l.strip()) > 3]
