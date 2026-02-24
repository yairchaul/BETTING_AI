from google.cloud import vision
import streamlit as st
import re

def get_vision_client():
    # Acceder a secrets de Streamlit
    creds_dict = dict(st.secrets["google_credentials"])
    return vision.ImageAnnotatorClient.from_service_account_info(creds_dict)

def extract_teams(text):
    lines = text.split("\n")
    equipos = []
    
    # Palabras a ignorar que suelen aparecer en OCR de casas de apuestas
    ignore_terms = ["empate", "vs", "vix", "en vivo", "mañana", "hoy", "apostar"]

    for line in lines:
        line = line.strip()
        # Limpiamos solo si la línea es puramente numérica (cuotas) 
        # pero mantenemos nombres de equipos con números
        if re.match(r'^[\d\.\+\-\s/]+$', line): 
            continue
            
        if len(line) > 3 and not any(term in line.lower() for term in ignore_terms):
            equipos.append(line)

    # Eliminar duplicados manteniendo el orden
    return list(dict.fromkeys(equipos))

def analyze_betting_image(uploaded_file):
    try:
        client = get_vision_client()
        content = uploaded_file.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        if response.error.message:
            st.error(f"Error de Google Vision: {response.error.message}")
            return []

        text = response.text_annotations[0].description
        return extract_teams(text)
    except Exception as e:
        st.error(f"Error en el procesamiento: {e}")
        return []
