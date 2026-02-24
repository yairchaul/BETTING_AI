import streamlit as st
from google.oauth2 import service_account
from google.cloud import vision
import io

def get_vision_client():
    try:
        # Extraemos las credenciales del diccionario de secretos
        creds_info = dict(st.secrets["google_credentials"])
        
        # LIMPIEZA DEFINITIVA DEL PEM: Elimina errores de longitud e invalid bytes
        pk = creds_info["private_key"].replace("\\n", "\n").strip()
        creds_info["private_key"] = pk
        
        credentials = service_account.Credentials.from_service_account_info(creds_info)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"Error de autenticación (PEM): {e}")
        return None

def analyze_betting_image(image_file):
    client = get_vision_client()
    if not client: 
        return []

    # Leemos el contenido de la imagen cargada
    image_file.seek(0)
    content = image_file.read()
    image = vision.Image(content=content)
    
    # Ejecutamos la detección de texto
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if not texts:
        return []

    # Procesamos el texto detectado
    # La primera entrada de 'texts' contiene todo el bloque de texto
    full_text = texts[0].description
    lineas = full_text.split('\n')
    
    # Filtro inteligente: ignoramos momios y palabras genéricas
    equipos_limpios = []
    palabras_ignorar = ["empate", "vs", "caliente", "apuesta", "liga"]
    
    for linea in lineas:
        linea_clean = linea.strip()
        # Evitamos números (momios como +400), líneas vacías o palabras de sistema
        if (len(linea_clean) > 3 and 
            not linea_clean.startswith(('-', '+')) and 
            not any(p in linea_clean.lower() for p in palabras_ignorar)):
            equipos_limpios.append(linea_clean)
            
    return equipos_limpios
