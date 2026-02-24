import streamlit as st
from google.oauth2 import service_account
from google.cloud import vision
import io

def get_vision_client():
    try:
        # Cargamos las credenciales desde los secretos de Streamlit
        creds_info = dict(st.secrets["google_credentials"])
        
        # CORRECCIÓN CRÍTICA: Convertir el texto de la llave en un formato PEM válido
        if "\\n" in creds_info["private_key"]:
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
    
    # Detectar texto en la imagen de la apuesta
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if not texts:
        return []

    # Extraer líneas de texto (equipos y momios)
    lineas = texts[0].description.split('\n')
    # Filtramos líneas cortas para quedarnos con nombres de equipos probables
    return [linea.strip() for linea in lineas if len(linea) > 3]
