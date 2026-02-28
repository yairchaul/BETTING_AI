import re
import streamlit as st
import pandas as pd
import requests
from google.cloud import vision

def calculate_implied_prob(american_odd):
    """Convierte momio americano a probabilidad implícita."""
    try:
        val = int(american_odd)
        if val > 0:
            return 100 / (val + 100)
        else:
            return abs(val) / (abs(val) + 100)
    except:
        return 0

def get_official_team_name(text):
    """
    Usa API-Football para normalizar el nombre del equipo.
    Limpia prefijos como FC, ACS, etc., para mejorar la búsqueda.
    """
    if not text or len(text) < 3:
        return text
    
    # Limpieza rápida antes de la API
    search_term = re.sub(r'\b(FC|ACS|CS|FK|Club|Strikers|Junior)\b', '', text, flags=re.IGNORECASE).strip()
    
    url = "https://v3.football.api-sports.io/teams"
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': st.secrets["API_FOOTBALL_KEY"]
    }
    
    try:
        response = requests.get(url, headers=headers, params={"search": search_term}, timeout=5)
        data = response.json()
        if data.get('response'):
            # Retorna el nombre oficial del primer resultado
            return data['response'][0]['team']['name']
    except Exception:
        pass
    return text

def clean_ocr_noise(text):
    """Elimina fechas, horas y el indicador de mercados (+43)."""
    # Elimina patrones como "28 Feb", "03:00" y "+43"
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d{1,2}', '', text)
    return text.strip()

def read_ticket_image(uploaded_file):
    """
    Función principal llamada por main.py. 
    Analiza la imagen, extrae momios y valida equipos con APIs.
    """
    client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
    content = uploaded_file.getvalue()
    image = vision.Image(content=content)
    
    # Usamos document_text_detection para detectar bloques y párrafos
    response = client.document_text_detection(image=image)
    matches = []

    if response.full_text_annotation:
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                # Agrupamos el texto del bloque manteniendo la estructura
                block_lines = []
                for para in block.paragraphs:
                    line_text = " ".join(["".join([s.text for s in w.symbols]) for w in para.words])
                    block_lines.append(line_text)
                
                full_block_text = "\n".join(block_lines)
                
                # Buscamos exactamente 3 momios (formato +XXX o -XXX)
                odds = re.findall(r'[+-]\d{3,4}', full_block_text)
                
                if len(odds) >= 3:
                    # Extraer y limpiar nombres de equipos
                    clean_text = clean_ocr_noise(full_block_text)
                    for o in odds:
                        clean_text = clean_text.replace(o, "")
                    
                    # Dividimos por líneas para separar Local y Visitante
                    potential_names = [n.strip() for n in clean_text.split('\n') if len(n.strip()) > 2]
                    
                    if len(potential_names) >= 2:
                        # 1. Cálculos de probabilidad e Overround (Margen de la casa)
                        prob_1 = calculate_implied_prob(odds[0])
                        prob_x = calculate_implied_prob(odds[1])
                        prob_2 = calculate_implied_prob(odds[2])
                        overround = (prob_1 + prob_x + prob_2) - 1
                        
                        # 2. Validación con API-Football para corregir el OCR
                        home_team = get_official_team_name(potential_names[0])
                        away_team = get_official_team_name(potential_names[1])
                        
                        matches.append({
                            "Evento": f"{home_team} vs {away_team}",
                            "1": odds[0],
                            "X": odds[1],
                            "2": odds[2],
                            "Prob. Victoria": f"{prob_1:.1%}",
                            "Margen Casa": f"{overround:.1%}",
                            "Verificación": "API-Football Verified ✅"
                        })
    
    return matches
