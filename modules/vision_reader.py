import re
from google.cloud import vision
import streamlit as st

def analyze_betting_image(uploaded_file):
    try:
        content = uploaded_file.getvalue()
        # Conexión directa a Google Vision (Asegúrate de tener st.secrets configurado)
        client = vision.ImageAnnotatorClient.from_service_account_info(st.secrets["google_credentials"])
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if not texts: return []

        # El OCR nos da un bloque de texto; lo procesamos por líneas
        full_text = texts[0].description
        lines = full_text.split('\n')
        
        games = []
        odd_pattern = r'[+-]\d{2,}' # Busca momios tipo +150, -200, +10

        for line in lines:
            odds = re.findall(odd_pattern, line)
            # Si la línea tiene al menos 2 momios, es un partido
            if len(odds) >= 2:
                # Limpiamos el texto para sacar nombres de equipos
                clean_name = re.sub(odd_pattern, '', line).replace('Empate', '').strip()
                teams = [t.strip() for t in clean_name.split('  ') if len(t.strip()) > 2]
                
                if len(teams) >= 2:
                    games.append({
                        "home": teams[0],
                        "away": teams[1],
                        "home_odd": odds[0],
                        "away_odd": odds[-1],
                        "draw_odd": odds[1] if len(odds) > 2 else "+250"
                    })
        return games
    except Exception as e:
        st.error(f"Error en Motor de Visión: {e}")
        return []
