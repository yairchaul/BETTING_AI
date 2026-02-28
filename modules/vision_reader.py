import re
import streamlit as st
import pandas as pd
import requests
from google.cloud import vision

def calculate_implied_prob(american_odd):
    """Convierte momio americano a probabilidad implícita."""
    try:
        val = int(str(american_odd).replace('+', ''))
        if val > 0:
            return 100 / (val + 100)
        else:
            return abs(val) / (abs(val) + 100)
    except:
        return 0.5

def get_official_team_name(text):
    """Normaliza el nombre usando API-Football."""
    if not text or len(text) < 3:
        return text
    
    # Limpieza de términos comunes para mejorar la búsqueda en la API
    search_term = re.sub(r'\b(FC|ACS|CS|FK|Club|Strikers|Junior|St|St\.)\b', '', text, flags=re.IGNORECASE).strip()
    
    url = "https://v3.football.api-sports.io/teams"
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': st.secrets.get("API_FOOTBALL_KEY", "")
    }
    
    try:
        response = requests.get(url, headers=headers, params={"search": search_term}, timeout=5)
        data = response.json()
        if data.get('response'):
            return data['response'][0]['team']['name']
    except:
        pass
    return text

def clean_ocr_noise(text):
    """Elimina fechas, horas e indicadores de mercados."""
    # Quita "28 Feb", "03:00", "+43"
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d+', '', text)
    return text.strip()

def read_ticket_image(uploaded_file):
    """
    Función principal exportada para main.py.
    Retorna una lista de diccionarios con la estructura esperada.
    """
    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        content = uploaded_file.getvalue()
        image = vision.Image(content=content)
        
        # document_text_detection es superior para capturas de pantalla con tablas
        response = client.document_text_detection(image=image)
        matches = []

        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    # Unir párrafos del bloque para mantener contexto horizontal
                    block_lines = []
                    for para in block.paragraphs:
                        line_text = " ".join(["".join([s.text for s in w.symbols]) for w in para.words])
                        block_lines.append(line_text)
                    
                    full_block_text = "\n".join(block_lines)
                    
                    # Detectar exactamente 3 momios (formato +123 o -123)
                    odds = re.findall(r'[+-]\d{3,4}', full_block_text)
                    
                    if len(odds) >= 3:
                        # Limpiar el bloque para obtener los nombres
                        clean_text = clean_ocr_noise(full_block_text)
                        for o in odds:
                            clean_text = clean_text.replace(o, "")
                        
                        # Extraer líneas de texto que no sean basura
                        potential_names = [n.strip() for n in clean_text.split('\n') if len(n.strip()) > 2]
                        
                        if len(potential_names) >= 2:
                            # Normalizar con API
                            home = get_official_team_name(potential_names[0])
                            away = get_official_team_name(potential_names[1])
                            
                            # Estructura compatible con tu main.py
                            matches.append({
                                "home": home,
                                "away": away,
                                "odds": odds[:3],
                                "context": f"{home} vs {away}", # Usado por tu 'rescate agresivo'
                                "prob_local": calculate_implied_prob(odds[0])
                            })
        
        return matches

    except Exception as e:
        st.error(f"Error crítico en OCR: {e}")
        return []
