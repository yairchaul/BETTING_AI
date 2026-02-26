import re
import os
import streamlit as st
from google.cloud import vision

def is_odd(text: str) -> bool:
    cleaned = re.sub(r'\s+', '', text.strip()).replace('+', '')
    try:
        val = int(cleaned)
        return abs(val) >= 100 or val == 0
    except: return False

def parse_row(row_words: list) -> dict | None:
    # Ordenar palabras horizontalmente para reconstruir la fila
    row_words.sort(key=lambda w: w["x"])
    texts = [w["text"] for w in row_words]
    
    odds = [t for t in texts if is_odd(t)]
    if len(odds) < 2: return None # Necesitamos al menos momio local y visitante
    
    # En la interfaz de Caliente: [Equipo Local] [Momio] [Empate] [Momio] [Equipo Visitante] [Momio]
    # Buscamos el texto que está ANTES del primer momio y DESPUÉS del último momio de equipo
    
    full_text = " ".join(texts)
    
    # Lógica de segmentación por posición de momios
    try:
        # El primer equipo termina donde empieza el primer momio
        home_parts = []
        for w in row_words:
            if is_odd(w["text"]): break
            if w["text"].lower() != "empate":
                home_parts.append(w["text"])
        
        # El segundo equipo empieza después del momio del empate o del centro
        away_parts = []
        found_center = False
        momios_encontrados = 0
        for w in row_words:
            if is_odd(w["text"]):
                momios_encontrados += 1
                continue
            if momios_encontrados >= 2: # Después del momio de Local y Empate
                if w["text"].lower() != "empate":
                    away_parts.append(w["text"])

        return {
            "home": " ".join(home_parts) if home_parts else "Local",
            "away": " ".join(away_parts) if away_parts else "Visitante",
            "all_odds": odds,
            "context": full_text
        }
    except:
        return None

def read_ticket_image(uploaded_file):
    content = uploaded_file.getvalue()
    client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    
    word_list = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = ''.join(s.text for s in word.symbols).strip()
                    v = word.bounding_box.vertices
                    word_list.append({
                        "text": word_text, 
                        "x": (v[0].x + v[2].x)/2, 
                        "y": (v[0].y + v[2].y)/2, 
                        "height": v[2].y - v[0].y
                    })

    if not word_list: return []
    
    # Agrupación por filas (eje Y)
    word_list.sort(key=lambda w: w["y"])
    rows, current_row = [], [word_list[0]]
    for w in word_list[1:]:
        if abs(w["y"] - current_row[-1]["y"]) < (current_row[-1]["height"] * 1.5):
            current_row.append(w)
        else:
            rows.append(current_row)
            current_row = [w]
    rows.append(current_row)

    matches = []
    for row_words in rows:
        match = parse_row(row_words)
        if match: matches.append(match)
    return matches
