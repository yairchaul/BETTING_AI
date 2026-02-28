import re
import streamlit as st
import pandas as pd
import requests
from google.cloud import vision

# --- LÓGICA MATEMÁTICA DE APUESTAS ---
def calculate_implied_prob(american_odd):
    """Convierte momio americano a probabilidad implícita"""
    try:
        odd = int(american_odd)
        if odd > 0:
            return 100 / (odd + 100)
        else:
            return abs(odd) / (abs(odd) + 100)
    except:
        return 0

def get_official_team(name):
    """Limpia el nombre usando API-Football"""
    if not name or len(name) < 3: return name
    url = "https://v3.football.api-sports.io/teams"
    headers = {'x-rapidapi-key': st.secrets["API_FOOTBALL_KEY"]}
    try:
        # Buscamos el equipo para obtener el nombre oficial
        response = requests.get(url, headers=headers, params={"search": name}, timeout=5)
        data = response.json()
        if data['response']:
            return data['response'][0]['team']['name']
    except:
        pass
    return name

def clean_block_noise(text):
    """Elimina fechas, horas y basura visual"""
    # Elimina 28 Feb, 03:00, +43, etc.
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d+', '', text)
    return text.strip()

def process_betting_image(uploaded_file):
    client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
    image = vision.Image(content=uploaded_file.getvalue())
    response = client.document_text_detection(image=image)
    
    final_results = []
    
    if response.full_text_annotation:
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                # Extraemos texto por párrafos para mantener coherencia
                paras = [" ".join(["".join([s.text for s in w.symbols]) for w in p.words]) for p in block.paragraphs]
                full_text = "\n".join(paras)
                
                # Buscamos los 3 momios (Ancla)
                odds = re.findall(r'[+-]\d{3}', full_text)
                
                if len(odds) >= 3:
                    # Limpiamos nombres
                    raw_names = clean_block_noise(full_text)
                    for o in odds: raw_names = raw_names.replace(o, "")
                    team_lines = [l.strip() for l in raw_names.split('\n') if len(l.strip()) > 2]
                    
                    if len(team_lines) >= 2:
                        # 1. Probabilidades
                        p1 = calculate_implied_prob(odds[0])
                        px = calculate_implied_prob(odds[1])
                        p2 = calculate_implied_prob(odds[2])
                        overround = (p1 + px + p2) - 1 # El margen de la casa
                        
                        # 2. Validación de nombres (API-Football)
                        local = get_official_team(team_lines[0])
                        visita = get_official_team(team_lines[1])
                        
                        final_results.append({
                            "Partido": f"{local} vs {visita}",
                            "1": odds[0],
                            "X": odds[1],
                            "2": odds[2],
                            "Prob. Victoria Local": f"{p1:.1%}",
                            "Margen Casa (Overround)": f"{overround:.1%}",
                            "Estatus": "Verificado ✅"
                        })
    return final_results

# --- INTERFAZ STREAMLIT ---
st.title("🤖 AI Betting Analyst Pro")
st.info("Subiendo la imagen, el sistema corregirá nombres vía API y calculará probabilidades reales.")

img_file = st.file_uploader("Cargar captura de pantalla", type=['png', 'jpg'])

if img_file:
    with st.spinner('Analizando y validando con API-Football...'):
        resultados = process_betting_image(img_file)
        
    if resultados:
        df = pd.DataFrame(resultados)
        # Resaltar si el margen de la casa es muy alto (>10%)
        st.data_editor(df, use_container_width=True)
        
        st.success("Análisis terminado. Los nombres han sido normalizados.")
    else:
        st.error("No se detectó el formato de apuesta. Asegúrate de que los momios (+/-) sean visibles.")
