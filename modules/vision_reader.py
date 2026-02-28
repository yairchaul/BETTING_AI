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
                            x = (v[0].x + v[2].x) / 2
                            y = (v[0].y + v[2].y) / 2
                            word_list.append({"text": word_text, "x": x, "y": y})

    except Exception as e:
        st.error(f"Google Vision falló: {str(e)}")
        return []

    if not word_list:
        st.error("No se extrajo texto.")
        return []

    # Ordenar por Y descendente (arriba a abajo)
    word_list.sort(key=lambda w: w["y"])

    matches = []
    debug = []

    i = 0
    while i < len(word_list) - 5:
        # Buscar patrón: nombre local + momios 3 cercanos en X
        current = word_list[i]
        if is_odd(current["text"]):
            i += 1
            continue

        # Posible local: palabra no-numérica
        if len(current["text"]) > 3 and not re.match(r'^\d', current["text"]):
            possible_home = current["text"]
            # Buscar 3 momios cercanos a la derecha y abajo
            odds = []
            for j in range(i+1, min(i+20, len(word_list))):
                t = word_list[j]["text"]
                if is_odd(t):
                    odds.append(t)
                if len(odds) == 3:
                    break

            if len(odds) == 3:
                # Intentar encontrar visitante (siguiente texto no-numérico después de momios)
                away = "Visitante"
                for k in range(j+1, min(j+20, len(word_list))):
                    t = word_list[k]["text"]
                    if not is_odd(t) and len(t) > 3 and not re.match(r'^\d', t):
                        away = t
                        break

                matches.append({
                    "home": possible_home,
                    "away": away,
                    "all_odds": odds,
                    "context": f"{possible_home} vs {away} → {odds}"
                })

                debug.append(f"{possible_home} vs {away} → {odds}")

                i = j + 1  # salta al siguiente bloque
                continue

        i += 1

    with st.expander("🔍 DEBUG OCR - Partidos Detectados", expanded=True):
        if debug:
            for d in debug:
                st.write(d)
        else:
            st.write("No se detectó patrón de 3 momios + nombre. ¿La imagen tiene columnas claras de 1 X 2?")

    return matches

def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)