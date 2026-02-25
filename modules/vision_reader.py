import re
import streamlit as st
from google.cloud import vision

def is_odd(text: str) -> bool:
    cleaned = re.sub(r'[^0-9+-]', '', text.strip())
    if not cleaned: return False
    try:
        val = int(cleaned)
        return abs(val) >= 100
    except: return False

def analyze_betting_image(uploaded_file):
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
                        "x": (v[0].x + v[2].x) / 2,
                        "y": (v[0].y + v[2].y) / 2
                    })

    # Detección de filas para el Debug
    word_list.sort(key=lambda w: w["y"])
    rows = []
    if word_list:
        curr = [word_list[0]]
        for w in word_list[1:]:
            if abs(w["y"] - curr[-1]["y"]) < 20: curr.append(w)
            else:
                rows.append(sorted(curr, key=lambda x: x["x"]))
                curr = [w]
        rows.append(curr)

    matches = []
    debug_data = []
    
    # Lógica de extracción (funciona para PC y móvil)
    for r in rows:
        texts = [w["text"] for w in r if len(w["text"]) >= 2]
        if len(texts) >= 3:
            debug_data.append(texts)
            odds = [t for t in texts if is_odd(t)]
            teams = [t for t in texts if not is_odd(t) and t.lower() not in ["empate", "x", "1", "2"]]
            
            if len(odds) >= 2 and len(teams) >= 2:
                matches.append({
                    "market": "1X2",
                    "home": teams[0],
                    "home_odd": odds[0],
                    "draw_odd": odds[1] if len(odds) > 2 else "+250",
                    "away": teams[1],
                    "away_odd": odds[-1]
                })

    return matches, debug_data
