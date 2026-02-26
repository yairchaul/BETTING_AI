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

def parse_row(texts: list) -> dict | None:
    odds = [t for t in texts if is_odd(t)]
    if not odds: return None
    
    # Filtramos nombres de equipos: longitud > 3, no momio, no "Empate"
    teams = [t for t in texts if not is_odd(t) and len(t) > 3 and t.lower() != "empate"]
    
    return {
        "home": teams[0] if len(teams) > 0 else "Local",
        "away": teams[1] if len(teams) > 1 else "Visitante",
        "all_odds": odds, # Enviamos todos los momios para mapeo
        "context": " ".join(texts)
    }

# Función principal que llama el main.py
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
                    word_list.append({"text": word_text, "x": (v[0].x + v[2].x)/2, "y": (v[0].y + v[2].y)/2, "height": v[2].y - v[0].y})

    if not word_list: return []
    
    word_list.sort(key=lambda w: w["y"])
    rows, current_row = [], [word_list[0]]
    for w in word_list[1:]:
        if abs(w["y"] - current_row[-1]["y"]) < (current_row[-1]["height"] * 1.5):
            current_row.append(w)
        else:
            rows.append(current_row); current_row = [w]
    rows.append(current_row)

    matches = []
    for row_words in rows:
        row_words.sort(key=lambda w: w["x"])
        texts = [w["text"] for w in row_words if len(w["text"]) >= 2]
        match = parse_row(texts)
        if match: matches.append(match)
    return matches
