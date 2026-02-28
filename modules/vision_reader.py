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

def is_team_name(text: str) -> bool:
    # Palabras largas, sin números, sin +/−, no fechas ni horas
    if len(text) < 4:
        return False
    if re.search(r'\d', text):
        return False
    if is_odd(text):
        return False
    if re.match(r'^\d{1,2}(:\d{2})?$', text):
        return False
    return True

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

    # Ordenar por Y (arriba a abajo) y luego por X (izquierda a derecha)
    word_list.sort(key=lambda w: (w["y"], w["x"]))

    matches = []
    debug = []

    i = 0
    while i < len(word_list):
        current = word_list[i]
        if is_team_name(current["text"]):
            home = current["text"]
            # Buscar los 3 momios más cercanos a la derecha o abajo
            odds = []
            j = i + 1
            while j < len(word_list) and len(odds) < 3:
                t = word_list[j]["text"]
                if is_odd(t):
                    odds.append(t)
                j += 1

            if len(odds) == 3:
                # Intentar encontrar visitante (siguiente nombre de equipo después de los momios)
                away = "Visitante"
                for k in range(j, len(word_list)):
                    t = word_list[k]["text"]
                    if is_team_name(t):
                        away = t
                        break

                matches.append({
                    "home": home,
                    "away": away,
                    "all_odds": odds,
                    "context": f"{home} vs {away} → {odds}"
                })

                debug.append(f"{home} vs {away} → {odds}")

                # Salta al siguiente posible nombre (después del visitante)
                i = k + 1 if 'k' in locals() else j
                continue

        i += 1

    with st.expander("🔍 DEBUG OCR - Partidos Detectados", expanded=True):
        if debug:
            for d in debug:
                st.write(d)
        else:
            st.write("No se encontraron nombres de equipo seguidos de 3 momios. ¿La imagen tiene texto claro y columnas visibles?")

    return matches

def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)