import streamlit as st
from google.oauth2 import service_account
from google.cloud import vision

def get_vision_client():
    try:
        # Extraemos las credenciales desde los secretos
        creds_info = dict(st.secrets["google_credentials"])
        
        # SANITIZACIÓN AUTOMÁTICA: Corrige el error InvalidLength(1625)
        pk = creds_info["private_key"].replace("\\n", "\n").strip()
        
        # Aseguramos los encabezados PEM para evitar InvalidByte(0, 92)
        if not pk.startswith("-----BEGIN"):
            pk = f"-----BEGIN PRIVATE KEY-----\n{pk}"
        if not pk.endswith("-----END PRIVATE KEY-----"):
            pk = f"{pk}\n-----END PRIVATE KEY-----"
            
        creds_info["private_key"] = pk
        credentials = service_account.Credentials.from_service_account_info(creds_info)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"Error de Autenticación Vision: {e}")
        return None

def analyze_betting_image(image_file):
    client = get_vision_client()
    if not client: return []
    
    # Procesamiento de imagen
    image_file.seek(0)
    content = image_file.read()
    image = vision.Image(content=content)
    
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if not texts: return []
    
    # Filtro: Extrae equipos ignorando momios (+/-) y texto corto
    lineas = texts[0].description.split('\n')
    return [l.strip() for l in lineas if len(l.strip()) > 3 and not l.strip().startswith(('-', '+'))]
