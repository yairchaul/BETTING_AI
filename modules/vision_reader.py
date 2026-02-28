import re
import streamlit as st
from google.cloud import vision

def procesar_texto_manual(texto):
    """Convierte 'Equipo A vs Equipo B' en un formato que el cerebro entienda."""
    partidos = []
    lineas = texto.split('\n')
    for linea in lineas:
        if " vs " in linea.lower():
            # Divide la línea por el separador 'vs' ignorando mayúsculas/minúsculas
            equipos = re.split(r'\s+vs\s+', linea, flags=re.IGNORECASE)
            if len(equipos) == 2:
                partidos.append({
                    "home": equipos[0].strip(),
                    "away": equipos[1].strip(),
                    "odds": ["+100", "+200", "+100"]  # Momios base para cálculo manual
                })
    return partidos

def clean_ocr_noise(text):
    """Limpia el texto extraído por Google Vision."""
    # Eliminar fechas, horas y marcadores de la interfaz
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d+', '', text)
    
    blacklist = ["Europa", "Rumania", "Turquía", "Italia", "Liga", "TFF", "Championship", "Resultado", "Final", "1", "X", "2"]
    lines = text.split('\n')
    return [l.strip() for l in lines if len(l.strip()) > 3 and not any(w in l for w in blacklist)]

def read_ticket_image(uploaded_file):
    """Intenta leer la imagen usando Google Vision API."""
    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        content = uploaded_file.getvalue()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        if not response.text_annotations: return []
        full_text = response.text_annotations[0].description
        
        all_odds = re.findall(r'[+-]\d{3,4}', full_text)
        lines = clean_ocr_noise(full_text)
        
        matches = []
        for i in range(0, len(lines) - 1, 2):
            idx_odd = (i // 2) * 3
            if idx_odd + 2 < len(all_odds):
                matches.append({
                    "home": lines[i],
                    "away": lines[i+1],
                    "odds": all_odds[idx_odd:idx_odd+3]
                })
        return matches
    except Exception as e:
        st.error(f"Error en OCR: {e}")
        return []
