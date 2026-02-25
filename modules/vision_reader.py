import re
import streamlit as st
from google.cloud import vision

def is_odd(text: str) -> bool:
    cleaned = re.sub(r'[^0-9+-]', '', text.strip())
    if not cleaned: return False
    try:
        val = int(cleaned)
        return abs(val) >= 100
    except:
        return False

def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    # Usamos tus secretos para Cloud Vision
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
                        "x": (v[0].x + v[2].x) / 2,
                        "y": (v[0].y + v[2].y) / 2
                    })

    if not word_list: return []

    matches = []
    word_list.sort(key=lambda w: w["y"])
    odds_found = [w for w in word_list if is_odd(w["text"])]
    
    # Agrupación por filas (cada 3 momios usualmente es un partido 1X2)
    for i in range(0, len(odds_found), 3):
        chunk = odds_found[i:i+3]
        if len(chunk) < 2: continue
        
        avg_y = sum(o["y"] for o in chunk) / len(chunk)
        # Filtramos palabras que están en la misma altura (Y) que los momios
        nearby_text = [w["text"] for w in word_list if abs(w["y"] - avg_y) < 40 and not is_odd(w["text"]) and len(w["text"]) > 3]
        
        if len(nearby_text) >= 2:
            matches.append({
                "home": nearby_text[0],
                "away": nearby_text[1],
                "home_odd": chunk[0]["text"],
                "draw_odd": chunk[1]["text"] if len(chunk) > 1 else "+200",
                "away_odd": chunk[2]["text"] if len(chunk) > 2 else "+100"
            })
    return matches
