import re
from google.cloud import vision
import streamlit as st

def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    client = vision.ImageAnnotatorClient.from_service_account_info(st.secrets["google_credentials"])
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts: return []

    lines = texts[0].description.split('\n')
    games = []
    
    # Patrón para detectar momios (+120, -110, etc)
    odd_pattern = r'[+-]\d{3,}'

    for line in lines:
        # Buscamos líneas que tengan al menos un momio
        odds = re.findall(odd_pattern, line)
        if len(odds) >= 2:
            # Limpiamos el texto para extraer nombres de equipos
            # Eliminamos los momios y la palabra "Empate" para no confundir al motor
            clean_text = re.sub(odd_pattern, '', line)
            clean_text = clean_text.replace('Empate', '').strip()
            
            # Dividimos lo que queda para intentar sacar Home y Away
            parts = [p.strip() for p in clean_text.split('  ') if len(p.strip()) > 2]
            
            if len(parts) >= 2:
                games.append({
                    "home": parts[0],
                    "away": parts[1],
                    "home_odd": odds[0],
                    "draw_odd": odds[1] if len(odds) > 2 else "+200",
                    "away_odd": odds[-1]
                })
    return games
