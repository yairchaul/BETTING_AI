import re
import streamlit as st
from google.cloud import vision

def is_odd(text: str) -> bool:
    cleaned = re.sub(r'\s+', '', text.strip())
    num_part = cleaned.replace('+', '').replace('-', '')
    try:
        val = float(num_part)
        return abs(val) >= 100 or (1 < val < 10)
    except:
        return False

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
                            x_center = (v[0].x + v[2].x) / 2
                            y_center = (v[0].y + v[2].y) / 2
                            word_list.append({"text": word_text, "x": x_center, "y": y_center})

    except Exception as e:
        st.error(f"Google Vision falló: {str(e)}")
        return []

    if not word_list:
        st.error("No se extrajo texto.")
        return []

    # Agrupar por filas horizontales (Y tolerancia baja para filas precisas)
    word_list.sort(key=lambda w: w["y"])
    rows = []
    current_row = [word_list[0]]
    for w in word_list[1:]:
        if abs(w["y"] - current_row[-1]["y"]) < 80:  # tolerancia ajustada
            current_row.append(w)
        else:
            rows.append(current_row)
            current_row = [w]
    rows.append(current_row)

    matches = []
    debug_rows = []

    for row in rows:
        row.sort(key=lambda w: w["x"])
        texts = [w["text"] for w in row]
        odds = [t for t in texts if is_odd(t)]
        if len(odds) < 3:
            continue

        # Limpiar texto no-momio para equipos
        non_odds = [t for t in texts if not is_odd(t) and len(t) > 2 and not re.match(r'^\d', t)]
        if len(non_odds) < 2:
            continue

        home = non_odds[0]
        away = " ".join(non_odds[1:]) if len(non_odds) > 1 else "Visitante"

        matches.append({
            "home": home,
            "away": away,
            "all_odds": odds[:3],
            "context": " ".join(texts)
        })

        debug_rows.append(f"{home} vs {away} → {odds[:3]}")

    with st.expander("🔍 DEBUG OCR - Partidos Detectados", expanded=True):
        for r in debug_rows:
            st.write(r)
        if not debug_rows:
            st.write("No se detectaron filas válidas. Intenta otra imagen o ajusta tolerancia.")

    return matches

def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)