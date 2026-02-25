import re
from google.cloud import vision
import streamlit as st

def analyze_betting_image(uploaded_file):
    try:
        content = uploaded_file.getvalue()
        # Usamos Google Vision puro, no Gemini, para evitar el error 404
        client = vision.ImageAnnotatorClient.from_service_account_info(st.secrets["google_credentials"])
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if not texts: return []

        full_text = texts[0].description
        lines = full_text.split('\n')
        games = []
        odd_pattern = r'[+-]\d{2,}' # Busca momios (+150, -200)

        for line in lines:
            odds = re.findall(odd_pattern, line)
            if len(odds) >= 2:
                # Limpiar texto para obtener equipos
                clean = re.sub(odd_pattern, '', line).replace('Empate', '').strip()
                teams = [t.strip() for t in clean.split('  ') if len(t.strip()) > 2]
                
                if len(teams) >= 2:
                    games.append({
                        "home": teams[0],
                        "away": teams[1],
                        "home_odd": odds[0],
                        "away_odd": odds[-1]
                    })
        return games
    except Exception as e:
        st.error(f"Error crítico de visión: {e}")
        return []
