import re
from google.cloud import vision
import streamlit as st

def analyze_betting_image(uploaded_file):
    try:
        # 1. Conexión usando las credenciales de los Secrets
        if "google_credentials" not in st.secrets:
            st.error("⚠️ No se encontraron las credenciales en Secrets.")
            return []

        content = uploaded_file.getvalue()
        client = vision.ImageAnnotatorClient.from_service_account_info(st.secrets["google_credentials"])
        
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if not texts:
            st.warning("No se detectó texto en la imagen.")
            return []

        # 2. Extracción de datos (Agnóstico)
        full_text = texts[0].description
        lines = full_text.split('\n')
        games = []
        odd_pattern = r'[+-]\d{2,}'

        for line in lines:
            odds = re.findall(odd_pattern, line)
            if len(odds) >= 2:
                # Limpiamos equipos
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
        st.error(f"Error de conexión: {e}")
        return []
