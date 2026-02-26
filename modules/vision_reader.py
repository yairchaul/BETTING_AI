import re
import io
import streamlit as st
from google.cloud import vision
from PIL import Image
import pytesseract


# =====================================
# UTILIDADES
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

    if "empate" in text_str or len([t for t in texts if is_odd(t)]) >= 2:
        return {"type": "1X2"}

    return {"type": "Unknown"}


# =====================================
# PARSER FILAS
# =====================================

def parse_row(texts: list) -> dict | None:

    market = detect_market_type(texts)

    if market["type"] == "1X2":

        if "Empate" in texts:
            idx_empate = texts.index("Empate")

            home = " ".join(texts[:idx_empate-1]).strip()
            home_odd = texts[idx_empate-1]
            draw_odd = texts[idx_empate+1]
            away = " ".join(texts[idx_empate+2:-1]).strip()
            away_odd = texts[-1]

            return {
                "market": "1X2",
                "home": home,
                "home_odd": home_odd,
                "draw_odd": draw_odd,
                "away": away,
                "away_odd": away_odd
            }

        odds = [t for t in texts if is_odd(t)]

        if len(odds) >= 3:
            return {
                "market": "1X2",
                "home": texts[0],
                "home_odd": odds[0],
                "draw_odd": odds[1],
                "away": texts[-2],
                "away_odd": odds[2]
            }

    return None


# =====================================
# OCR PRINCIPAL (GOOGLE VISION)
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
        return []

    # ===== Detectar filas =====
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

    # ===== Horizontal =====
    for row_words in rows:

        row_words.sort(key=lambda w: w["x"])

        texts = [w["text"] for w in row_words if len(w["text"]) >= 2]

        if len(texts) < 3:
            continue

        debug_rows.append(texts)

        match = parse_row(texts)

        if match:
            matches.append(match)

    # ===== Vertical fallback =====
    if len(matches) == 0:

        for i in range(len(rows) - 2):

            combined = rows[i] + rows[i+1] + rows[i+2]

            combined_texts = [w["text"] for w in combined]

            odds = [t for t in combined_texts if is_odd(t)]

            if len(odds) >= 2:

                teams = [
                    t for t in combined_texts
                    if not is_odd(t) and len(t) > 3
                ]

                if len(teams) >= 2:
                    matches.append({
                        "market": "1X2",
                        "home": teams[0],
                        "home_odd": odds[0],
                        "draw_odd": odds[1] if len(odds) > 1 else "+250",
                        "away": teams[1],
                        "away_odd": odds[2] if len(odds) > 2 else "+150"
                    })

    with st.expander("🔍 DEBUG OCR", expanded=False):
        for r in debug_rows:
            st.write(r)

    return matches


# =====================================
# COMPATIBILIDAD EV ELITE
# =====================================

def read_ticket_image(uploaded_file):
    """
    Alias para compatibilidad con main.py
    """
    return analyze_betting_image(uploaded_file)
