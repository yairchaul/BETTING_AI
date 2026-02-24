import streamlit as st
from google.oauth2 import service_account
from google.cloud import vision
import io

def get_vision_client():
    try:
        # Cargamos las credenciales desde los secretos
        creds_info = dict(st.secrets["google_credentials"])
        
        # LIMPIEZA CRÍTICA: Eliminamos cualquier problema de formato en la llave
        # Esto soluciona el error InvalidLength(1625)
        pk = creds_info["private_key"]
        pk = pk.replace("\\n", "\n").strip()
        
        # Aseguramos que los encabezados PEM sean correctos
        if not pk.startswith("-----BEGIN PRIVATE KEY-----"):
            pk = f"-----BEGIN PRIVATE KEY-----\n{pk}"
        if not pk.endswith("-----END PRIVATE KEY-----"):
            pk = f"{pk}\n-----END PRIVATE KEY-----"
            
        creds_info["private_key"] = pk
        
        credentials = service_account.Credentials.from_service_account_info(creds_info)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"Error de autenticación: {e}")
        return None

def analyze_betting_image(image_file):
    client = get_vision_client()
    if not client: return []

    # Leemos la imagen cargada por el usuario
    image_file.seek(0)
    content = image_file.read()
    image = vision.Image(content=content)
    
    # Análisis de texto mediante IA
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if not texts: return []

    # Extraemos equipos y momios (ej: Atlético Madrid -264)
    lineas = texts[0].description.split('\n')
    return [l.strip() for l in lineas if len(l.strip()) > 3]
