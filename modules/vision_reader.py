import re
import streamlit as st
from google.cloud import vision


# ==============================
# UTILIDADES
# ==============================

def is_odd(text: str) -> bool:
    cleaned = text.strip().replace("+", "").replace("-", "")
    try:
        val = float(cleaned)
        return abs(val) >= 100
    except:
        return False


def clean_text(text):
    """
    Limpieza fuerte para eliminar fechas, horas y ruido.
    """

    # Ignorar números puros (ej: 28)
    if re.fullmatch(r"\d+", text):
        return ""

    # Ignorar horas (ej: 14:00)
    if re.fullmatch(r"\d{1,2}:\d{2}", text):
        return ""

    # Ignorar meses
    if re.fullmatch(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", text, re.IGNORECASE):
        return ""

    # Ignorar palabras muy cortas
    if len(text) <= 2:
        return ""

    # Mantener solo letras
    text = re.sub(r"[^A-Za-zÁÉÍÓÚáéíóúÑñ]", "", text)

    return text.strip()


def cluster_match_blocks(word_list, block_tolerance=140):
    """
    Agrupa palabras en bloques verticales completos usando
    promedio dinámico de coordenadas Y.
    """

    if not word_list:
        return []

    word_list.sort(key=lambda w: w["y"])

    blocks = []
    current_block = [word_list[0]]
    current_avg_y = word_list[0]["y"]

    for word in word_list[1:]:
        if abs(word["y"] - current_avg_y) < block_tolerance:
            current_block.append(word)
            current_avg_y = sum(w["y"] for w in current_block) / len(current_block)
        else:
            blocks.append(current_block)
            current_block = [word]
            current_avg_y = word["y"]

    blocks.append(current_block)

    return blocks


# ==============================
# MOTOR PRINCIPAL OCR
# ==============================

def analyze_betting_image(uploaded_file):

    content = uploaded_file.getvalue()
    word_list = []

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
                            y_center = (v[0].y + v[2].y) / 2
                            x_center = (v[0].x + v[2].x) / 2

                            word_list.append({
                                "text": word_text,
                                "x": x_center,
                                "y": y_center
                            })

    except Exception as e:
        st.error(f"Google Vision falló: {str(e)}")
        return []

    if not word_list:
        st.error("No se extrajo texto.")
        return []

    # 🔥 AGRUPAR POR BLOQUES VERTICALES GRANDES
    blocks = cluster_match_blocks(word_list, block_tolerance=140)

    matches = []

    for block in blocks:

        block.sort(key=lambda w: w["y"])

        odds = [w["text"] for w in block if is_odd(w["text"])]

        if len(odds) < 3:
            continue

        odds = odds[:3]

        words_only = []

        for w in block:
            if not is_odd(w["text"]):
                cleaned = clean_text(w["text"])
                if cleaned:
                    words_only.append(cleaned)

        if len(words_only) < 2:
            continue

        home = words_only[0]
        away = words_only[1]

        matches.append({
            "home": home,
            "away": away,
            "all_odds": odds
        })

    # ==============================
    # DEBUG
    # ==============================

    with st.expander("🔍 DEBUG OCR - Partidos Detectados", expanded=True):
        if matches:
            for m in matches:
                st.write(f"{m['home']} vs {m['away']} → {m['all_odds']}")
        else:
            st.write("No se detectaron partidos válidos.")

    return matches


def read_ticket_image(uploaded_file):
    return analyze_betting_image(uploaded_file)