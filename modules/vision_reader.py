# VERSION_SYNC: 4.0_FINAL_RESCUE
import re
import streamlit as st
from google.cloud import vision

def clean_ocr_noise(text):
    """Limpia fechas, horas y basura visual como '+ 43'"""
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d+', '', text)
    return text.strip()

def read_ticket_image(uploaded_file):
    """
    Función optimizada para leer capturas de Caliente/Bet365 
    donde los momios están separados de los nombres.
    """
    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        content = uploaded_file.getvalue()
        image = vision.Image(content=content)
        
        # Obtenemos TODO el texto de la imagen de una vez
        response = client.text_detection(image=image)
        if not response.text_annotations:
            return []

        # El primer elemento de text_annotations contiene todo el texto detectado en orden
        full_page_text = response.text_annotations[0].description
        
        # Buscamos TODOS los momios americanos en la página (+/- seguido de 3 o 4 números)
        all_odds = re.findall(r'[+-]\d{3,4}', full_page_text)
        
        # Limpiamos el texto de los momios detectados para aislar los nombres
        clean_text = full_page_text
        for o in all_odds:
            clean_text = clean_text.replace(o, "")
        
        clean_text = clean_ocr_noise(clean_text)
        
        # Extraemos líneas que parecen nombres de equipos (más de 3 letras)
        # Filtramos palabras genéricas de la interfaz
        ignore_words = ["Resultado", "Final", "Empate", "Local", "Visitante", "Europa", "Liga"]
        lines = [
            l.strip() for l in clean_text.split('\n') 
            if len(l.strip()) > 3 and not any(w in l for w in ignore_words)
        ]

        matches = []
        # Agrupamos de 2 en 2 equipos y de 3 en 3 momios
        # Esta lógica asume que el OCR lee de arriba a abajo y de izquierda a derecha
        for i in range(0, len(lines) - 1, 2):
            odd_index = (i // 2) * 3
            if odd_index + 2 < len(all_odds):
                matches.append({
                    "home": lines[i],
                    "away": lines[i+1],
                    "odds": [all_odds[odd_index], all_odds[odd_index+1], all_odds[odd_index+2]],
                    "context": f"{lines[i]} vs {lines[i+1]}"
                })
        
        return matches

    except Exception as e:
        st.error(f"Error en la extracción: {e}")
        return []
