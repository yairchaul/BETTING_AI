import re
import os
import streamlit as st
from google.cloud import vision
from PIL import Image

# =====================================
# SAFE PYTESSERACT IMPORT
# =====================================
try:
    import pytesseract
    if os.name != "nt":
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    TESSERACT_AVAILABLE = True
except Exception:
    TESSERACT_AVAILABLE = False

# =====================================
# UTILIDADES DE DETECCIÓN
# =====================================
def is_odd(text: str) -> bool:
    """Detecta si el texto es un momio (+100, -150, etc)"""
    cleaned = re.sub(r'\s+', '', text.strip()).replace('+', '')
    try:
        val = float(cleaned)
        # Filtro para momios americanos típicos o decimales bajos
        return abs(val) >= 100 or val == 0 or (1.0 < val < 10.0)
    except:
        return False

def parse_row_smart(row_words: list) -> dict | None:
    """
    Separa Local y Visitante usando los momios como anclas.
    Estructura: [EQUIPO LOCAL] [MOMIO] [EMPATE] [MOMIO] [EQUIPO VISITANTE] [MOMIO]
    """
    row_words.sort(key=lambda w: w["x"])
    
    # Identificamos índices de palabras que son momios
    odds_indices = [i for i, w in enumerate(row_words) if is_odd(w["text"])]
    
    if len(odds_indices) < 2:
        return None

    try:
        # Local: Todo antes del primer momio (saltando 'Empate')
        home_parts = [w["text"] for i, w in enumerate(row_words) 
                      if i < odds_indices[0] and w["text"].lower() != "empate"]
        
        # Visitante: Todo después del segundo momio (momio de empate)
        away_parts = []
        momios_vistos = 0
        for w in row_words:
            if is_odd(w["text"]):
                momios_vistos += 1
                continue
            if momios_vistos >= 2: # Estamos después del momio de Local y del Empate
                if w["text"].lower() != "empate":
                    away_parts.append(w["text"])

        all_odds = [w["text"] for i, w in enumerate(row_words) if i in odds_indices]

        return {
            "home": " ".join(home_parts).strip() if home_parts else "Local",
            "away": " ".join(away_parts).strip() if away_parts else "Visitante",
            "all_odds": all_odds,
            "context": " ".join([w["text"] for w in row_words])
        }
    except:
        return None

# =====================================
# GOOGLE VISION + PROCESAMIENTO
# =====================================
def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    client = vision.ImageAnnotatorClient.from_service_account_info(
        dict(st.secrets["google_credentials"])
    )
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

    if not word_list:
        # Fallback Tesseract si Google Vision no detecta nada
        if TESSERACT_AVAILABLE:
            st.warning("Usando Fallback Tesseract...")
            # (Lógica de Tesseract aquí si fuera necesaria)
        return []

    # Agrupar por filas (Eje Y)
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
    debug_rows = []
    for row_words in rows:
        match = parse_row_smart(row_words)
        if match:
            matches.append(match)
            debug_rows.append(match["context"])

    with st.expander("🔍 DEBUG OCR - Filas Detectadas", expanded=False):
        for r in debug_rows:
            st.write(r)

    return matches

def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)
