import re
import os
import streamlit as st
from google.cloud import vision
from PIL import Image

# =====================================
# SAFE PYTESSERACT IMPORT
# =====================================
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    if os.name != "nt":
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    TESSERACT_AVAILABLE = True
except Exception:
    pass  # Silencioso, warning más abajo si hace falta

# =====================================
# UTILIDADES DE DETECCIÓN
# =====================================
def is_odd(text: str) -> bool:
    """Detecta momios americanos (+150, -200, etc)"""
    cleaned = re.sub(r'\s+', '', text.strip())
    # Quitamos + y - para probar conversión numérica
    num_part = cleaned.replace('+', '').replace('-', '')
    try:
        val = float(num_part)
        return abs(val) >= 100 or val == 0 or (1.0 < val < 10.0)
    except:
        return False

def parse_row_smart(row_words: list) -> dict | None:
    """
    Intenta separar local / empate / visitante usando momios y 'X'/'Empate'
    """
    row_words.sort(key=lambda w: w["x"])
    
    # Buscamos índices de momios
    odds_indices = [i for i, w in enumerate(row_words) if is_odd(w["text"])]
    
    # Buscamos índice aproximado de 'X' o 'Empate'
    empate_idx = next((i for i, w in enumerate(row_words) if w["text"].upper() in ["X", "EMPATE"]), -1)
    
    if len(odds_indices) < 2:
        return None

    try:
        # Local: todo antes del primer momio o antes de 'X'
        cut_idx = min(odds_indices[0], empate_idx if empate_idx != -1 else len(row_words))
        home_parts = [w["text"] for i, w in enumerate(row_words) if i < cut_idx and w["text"].lower() not in ["x", "empate"]]

        # Visitante: después del último momio
        away_start = max(odds_indices) + 1
        away_parts = [w["text"] for i, w in enumerate(row_words) if i >= away_start]

        # Momios encontrados
        all_odds = [w["text"] for i, w in enumerate(row_words) if i in odds_indices]

        return {
            "home": " ".join(home_parts).strip() or "Local",
            "away": " ".join(away_parts).strip() or "Visitante",
            "all_odds": all_odds,
            "context": " ".join([w["text"] for w in row_words])
        }
    except Exception as e:
        st.warning(f"Error parseando fila: {str(e)}")
        return None

# =====================================
# GOOGLE VISION + PROCESAMIENTO
# =====================================
def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    
    word_list = []  # Siempre existe
    
    # Intento principal: Google Cloud Vision
    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(
            dict(st.secrets["google_credentials"])
        )
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        
        if response.full_text_annotation and response.full_text_annotation.pages:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = ''.join(s.text for s in word.symbols).strip()
                            if not word_text:
                                continue
                            v = word.bounding_box.vertices
                            word_list.append({
                                "text": word_text,
                                "x": (v[0].x + v[2].x) / 2,
                                "y": (v[0].y + v[2].y) / 2,
                                "height": v[2].y - v[0].y
                            })
    
    except Exception as e:
        st.error(f"Google Vision falló: {str(e)}")
    
    # Fallback: Tesseract si Vision no dio nada
    if not word_list and TESSERACT_AVAILABLE:
        st.warning("Vision no detectó → usando Tesseract")
        try:
            img = Image.open(uploaded_file)
            data = pytesseract.image_to_data(img, lang='eng+spa', output_type=pytesseract.Output.DICT)
            n_boxes = len(data['level'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 35 and data['text'][i].strip():
                    x = data['left'][i] + data['width'][i] / 2
                    y = data['top'][i] + data['height'][i] / 2
                    h = data['height'][i]
                    word_list.append({
                        "text": data['text'][i].strip(),
                        "x": x,
                        "y": y,
                        "height": h
                    })
        except Exception as te:
            st.error(f"Tesseract falló: {str(te)}")
    
    if not word_list:
        st.error("No se extrajo texto alguno de la imagen.")
        return []

    # Agrupar palabras en filas por coordenada Y
    word_list.sort(key=lambda w: w["y"])
    rows, current_row = [], [word_list[0]]
    for w in word_list[1:]:
        if abs(w["y"] - current_row[-1]["y"]) < (current_row[-1]["height"] * 1.8):  # tolerancia aumentada
            current_row.append(w)
        else:
            rows.append(current_row)
            current_row = [w]
    rows.append(current_row)

    matches = []
    debug_rows = []
    for row_words in rows:
        if len(row_words) < 3:
            continue  # fila muy corta → ruido
        match = parse_row_smart(row_words)
        if match:
            matches.append(match)
            debug_rows.append(match["context"])

    with st.expander("🔍 DEBUG OCR - Filas Detectadas", expanded=True):
        if debug_rows:
            for r in debug_rows:
                st.write(r)
        else:
            st.write("Ninguna fila parseada correctamente.")

    return matches

def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)