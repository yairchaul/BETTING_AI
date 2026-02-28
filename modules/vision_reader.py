import re
import streamlit as st
from google.cloud import vision
from collections import defaultdict

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
                            x = (v[0].x + v[2].x) / 2
                            y = (v[0].y + v[2].y) / 2
                            word_list.append({"text": word_text, "x": x, "y": y})

    except Exception as e:
        st.error(f"Google Vision falló: {str(e)}")
        return []

    if not word_list:
        st.error("No se extrajo texto.")
        return []

    # Ordenar por Y descendente (de arriba a abajo)
    word_list.sort(key=lambda w: w["y"])

    # Agrupar por líneas horizontales (tolerancia 50 px)
    rows = []
    current_row = []
    last_y = None

    for w in word_list:
        if last_y is None or abs(w["y"] - last_y) < 50:
            current_row.append(w)
        else:
            if current_row:
                rows.append(current_row)
            current_row = [w]
        last_y = w["y"]
    if current_row:
        rows.append(current_row)

    matches = []
    debug = []

    for row in rows:
        # Ordenar por X (izquierda a derecha)
        row.sort(key=lambda w: w["x"])
        texts = [w["text"] for w in row]
        odds = [t for t in texts if is_odd(t)]

        if len(odds) != 3:
            continue  # Solo filas con exactamente 3 momios

        # Buscar texto no-numérico antes del primer momio (local)
        non_odds_before = []
        for t in texts:
            if is_odd(t):
                break
            if len(t) > 2 and not re.match(r'^\d', t):
                non_odds_before.append(t)

        home = " ".join(non_odds_before) if non_odds_before else "Local"

        # Visitante: texto después del último momio
        non_odds_after = []
        started_after = False
        for t in texts[::-1]:  # desde el final
            if is_odd(t):
                started_after = True
                continue
            if started_after and len(t) > 2 and not re.match(r'^\d', t):
                non_odds_after.append(t)
        away = " ".join(reversed(non_odds_after)) if non_odds_after else "Visitante"

        matches.append({
            "home": home,
            "away": away,
            "all_odds": odds,
            "context": " ".join(texts)
        })

        debug.append(f"{home} vs {away} → {odds}")

    with st.expander("🔍 DEBUG OCR - Partidos Detectados", expanded=True):
        for d in debug:
            st.write(d)
        if not debug:
            st.write("No se detectaron filas con 3 momios. Intenta otra captura o ajusta tolerancia Y.")

    return matches

def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)