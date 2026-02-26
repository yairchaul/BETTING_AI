import re
import io
import os
import streamlit as st
from google.cloud import vision
from PIL import Image

# =====================================
# SAFE PYTESSERACT IMPORT (NO CRASH)
# =====================================
try:
    import pytesseract
    if os.name != "nt":
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    TESSERACT_AVAILABLE = True
except Exception:
    TESSERACT_AVAILABLE = False

# =====================================
# UTILIDADES MEJORADAS
# =====================================
def is_odd(text: str) -> bool:
    cleaned = re.sub(r'\s+', '', text.strip()).replace('+', '')
    try:
        val = int(cleaned)
        return abs(val) >= 100 or val == 0
    except:
        return False

def detect_market_type(texts: list) -> dict:
    text_str = " ".join(texts).lower()
    # Detección de mercados específicos de Caliente
    if "ambos" in text_str: return {"type": "BTTS"}
    if "total" in text_str or "over" in text_str or "under" in text_str: return {"type": "OU"}
    if "empate" in text_str or len([t for t in texts if is_odd(t)]) >= 2:
        return {"type": "1X2"}
    return {"type": "Unknown"}

# =====================================
# PARSER FILAS (Ahora reconoce más que 1X2)
# =====================================
def parse_row(texts: list) -> dict | None:
    market = detect_market_type(texts)
    odds = [t for t in texts if is_odd(t)]
    
    if not odds: return None

    # Caso 1X2 (Resultado Final)
    if market["type"] == "1X2":
        if "Empate" in texts:
            idx = texts.index("Empate")
            return {
                "market": "1X2",
                "home": " ".join(texts[:idx-1]).strip(),
                "home_odd": texts[idx-1],
                "draw_odd": texts[idx+1],
                "away": " ".join(texts[idx+2:-1]).strip(),
                "away_odd": texts[-1]
            }
        elif len(odds) >= 3:
            return {
                "market": "1X2", "home": texts[0], "away": texts[-2],
                "home_odd": odds[0], "draw_odd": odds[1], "away_odd": odds[2]
            }

    # Caso Goles o Ambos Anotan (Detecta la cuota y el contexto)
    if market["type"] in ["BTTS", "OU"] and len(odds) >= 1:
        return {
            "market": market["type"],
            "home": texts[0], # Intento de capturar equipo
            "away": "Generic", 
            "odds": {texts[texts.index(odds[0])-1] if texts.index(odds[0])>0 else "Cuota": odds[0]}
        }

    return None

# [Mantener funciones analyze_betting_image y read_ticket_image igual a tu original]
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
                        "y": (v[0].y + v[2].y) / 2,
                        "height": v[2].y - v[0].y
                    })

    if not word_list: return []

    word_list.sort(key=lambda w: w["y"])
    rows = []
    current_row = [word_list[0]]
    for w in word_list[1:]:
        if abs(w["y"] - current_row[-1]["y"]) < (current_row[-1]["height"] * 1.5):
            current_row.append(w)
        else:
            rows.append(current_row)
            current_row = [w]
    rows.append(current_row)

    matches = []
    debug_rows = []
    for row_words in rows:
        row_words.sort(key=lambda w: w["x"])
        texts = [w["text"] for w in row_words if len(w["text"]) >= 2]
        if len(texts) < 3: continue
        debug_rows.append(texts)
        match = parse_row(texts)
        if match: matches.append(match)

    with st.expander("🔍 DEBUG OCR", expanded=False):
        for r in debug_rows: st.write(r)

    return matches

def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)
