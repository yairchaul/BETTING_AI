import re
import os
import streamlit as st
from google.cloud import vision
from PIL import Image

TESSERACT_AVAILABLE = False
try:
    import pytesseract
    if os.name != "nt":
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    TESSERACT_AVAILABLE = True
except Exception:
    pass

def is_odd(text: str) -> bool:
    cleaned = re.sub(r'\s+', '', text.strip())
    num_part = cleaned.replace('+', '').replace('-', '')
    try:
        val = float(num_part)
        return abs(val) >= 100 or val == 0 or (1.0 < val < 10.0)
    except:
        return False

def parse_row_smart(row_words: list) -> dict | None:
    row_words.sort(key=lambda w: w["x"])
    
    odds_indices = [i for i, w in enumerate(row_words) if is_odd(w["text"])]
    if len(odds_indices) < 3:  # Esperamos mínimo 3 momios
        return None

    empate_idx = next((i for i, w in enumerate(row_words) if w["text"].upper() in ["X", "EMPATE"]), -1)

    try:
        # Local: palabras antes del primer momio o 'X'
        cut_idx = min(odds_indices[0], empate_idx if empate_idx != -1 else len(row_words))
        home_parts = [w["text"] for i, w in enumerate(row_words) if i < cut_idx and w["text"].lower() not in ["x", "empate"]]

        # Visitante: palabras después del último momio
        away_start = max(odds_indices) + 1
        away_parts = [w["text"] for i, w in enumerate(row_words) if i >= away_start]

        all_odds = [row_words[i]["text"] for i in odds_indices]

        return {
            "home": " ".join(home_parts).strip() or "Local",
            "away": " ".join(away_parts).strip() or "Visitante",
            "all_odds": all_odds,
            "context": " ".join(w["text"] for w in row_words)
        }
    except:
        return None

def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    word_list = []

    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
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

    if not word_list and TESSERACT_AVAILABLE:
        st.warning("Vision falló → Tesseract")
        try:
            img = Image.open(uploaded_file)
            data = pytesseract.image_to_data(img, lang='eng+spa', output_type=pytesseract.Output.DICT)
            for i in range(len(data['level'])):
                if int(data['conf'][i]) > 35 and data['text'][i].strip():
                    x = data['left'][i] + data['width'][i] / 2
                    y = data['top'][i] + data['height'][i] / 2
                    h = data['height'][i]
                    word_list.append({"text": data['text'][i].strip(), "x": x, "y": y, "height": h})
        except Exception as te:
            st.error(f"Tesseract falló: {str(te)}")

    if not word_list:
        st.error("No se extrajo texto.")
        return []

    word_list.sort(key=lambda w: w["y"])
    rows, current_row = [], [word_list[0]]
    for w in word_list[1:]:
        if abs(w["y"] - current_row[-1]["y"]) < current_row[-1]["height"] * 1.8:
            current_row.append(w)
        else:
            rows.append(current_row)
            current_row = [w]
    rows.append(current_row)

    matches = []
    debug_rows = []
    for row in rows:
        if len(row) < 5: continue
        match = parse_row_smart(row)
        if match:
            matches.append(match)
            debug_rows.append(f"{match['home']} vs {match['away']} → {match['all_odds']}")

    with st.expander("🔍 DEBUG OCR - Filas Detectadas", expanded=True):
        for r in debug_rows:
            st.write(r)
        if not debug_rows:
            st.write("Ninguna fila válida.")

    return matches

def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)