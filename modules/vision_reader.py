import re
import streamlit as st
from google.cloud import vision

def clean_ocr_noise(text):
    """Elimina ruidos de la interfaz y nombres de ligas."""
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d+', '', text)
    
    # Lista negra para que no confunda ligas con equipos
    blacklist = [
        "Europa", "Rumania", "Turquía", "Italia", "Liga 2", "Liga 3", 
        "TFF League", "Primavera", "Championship", "Resultado", "Final", 
        "1", "X", "2", "Directo", "Hoy", "Mañana"
    ]
    for word in blacklist:
        text = text.replace(word, "")
    
    return text.strip()

def read_ticket_image(uploaded_file):
    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        content = uploaded_file.getvalue()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        if not response.text_annotations: return []
        full_text = response.text_annotations[0].description
        
        all_odds = re.findall(r'[+-]\d{3,4}', full_text)
        clean_text = clean_ocr_noise(full_text)
        for o in all_odds: clean_text = clean_text.replace(o, "")
        
        lines = [l.strip() for l in clean_text.split('\n') if len(l.strip()) > 3]
        
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
        st.error(f"Error OCR: {e}")
        return []
