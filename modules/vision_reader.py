import streamlit as st
from google.oauth2 import service_account
from google.cloud import vision

def get_vision_client():
    try:
        # Extraemos el diccionario de credenciales de los secretos
        creds_dict = st.secrets["google_credentials"]
        
        # EL PASO CLAVE: Reemplazar los \n de texto por saltos de línea reales
        # Esto soluciona el error "InvalidByte" o "InvalidLength"
        formatted_key = creds_dict["private_key"].replace("\\n", "\n")
        creds_dict["private_key"] = formatted_key
        
        # Crear las credenciales de forma segura
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"Error de configuración: Hubo un problema al procesar la imagen: {e}")
        return None

# Uso en tu función de análisis
def analyze_betting_image(image_file):
    client = get_vision_client()
    if client is None:
        return None
    # ... resto de tu código de análisis ...
