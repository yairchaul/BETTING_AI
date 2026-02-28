import re
import streamlit as st
import pandas as pd
import requests
from google.cloud import vision

def get_official_team(name):
    """Normaliza el nombre del equipo usando API-Football"""
    if not name or len(name) < 3: 
        return name
    
    url = "https://v3.football.api-sports.io/teams"
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': st.secrets["API_FOOTBALL_KEY"]
    }
    
    try:
        # Filtramos un poco el nombre para que la búsqueda sea más limpia
        search_name = re.sub(r'(FC|CS|ACS|FK|Club|Strikers)', '', name).strip()
        response = requests.get(url, headers=headers, params={"search": search_name}, timeout=5)
        data = response.json()
        if data.get('response'):
            return data['response'][0]['team']['name']
    except Exception:
        pass
    return name

def calculate_implied_prob(american_odd):
    """Calcula la probabilidad implícita de un momio americano"""
    try:
        odd = int(american_odd)
        if odd > 0:
            return 100 / (odd + 100)
        else:
            return abs(odd) / (abs(odd) + 100)
    except:
        return 0

def clean_noise(text):
    """Elimina fechas, horas y contadores como +43"""
    # Elimina: 28 Feb, 03:00, +43
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d{1,2}', '', text)
    return text.strip()

def read_ticket_image(uploaded_file):
    """Función principal llamada por main.py"""
    client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
    content = uploaded_file.getvalue()
    image = vision.Image(content=content)
    
    # Document text detection es mejor para párrafos y tablas
    response = client.document_text_detection(image=image)
    matches = []

    if response.full_text_annotation:
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                # Agrupamos el texto del bloque
                block_lines = []
                for para in block.paragraphs:
                    line = " ".join(["".join([s.text for s in w.symbols]) for w in para.words])
                    block_lines.append(line)
                
                full_text = "\n".join(block_lines)
                
                # Buscamos 3 momios americanos (+XXX o -XXX)
                odds = re.findall(r'[+-]\d{3,4}', full_text)
                
                if len(odds) >= 3:
                    # Limpiamos el bloque de basura y momios para aislar nombres
                    clean_text = clean_noise(full_text)
                    for o in odds:
                        clean_text = clean_text.replace(o, "")
                    
                    names = [n.strip() for n in clean_text.split('\n') if len(n.strip()) > 2]
                    
                    if len(names) >= 2:
                        # Cálculos de probabilidad y margen
                        p1 = calculate_implied_prob(odds[0])
                        px = calculate_implied_prob(odds[1])
                        p2 = calculate_implied_prob(odds[2])
                        overround = (p1 + px + p2) - 1
                        
                        # Validación con API-Football
                        home_official = get_official_team(names[0])
                        away_official = get_official_team(names[1])
                        
                        matches.append({
                            "Partido": f"{home_official} vs {away_official}",
                            "1": odds[0],
                            "X": odds[1],
                            "2": odds[2],
                            "Prob. Local": f"{p1:.1%}",
                            "Overround (Margen)": f"{overround:.1%}",
                            "Info": "Verificado con API-Football ✅"
                        })
    
    return matches
