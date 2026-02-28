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
    Limpieza fuerte para eliminar fechas, horas, números y ruido.
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


def cluster_rows(word_list, tolerance=18):
    """
    Agrupa palabras en filas reales usando proximidad vertical.
    """
    rows = []
    word_list.sort(key=lambda w: w["y"])

    for word in word_list:
        placed = False

        for row in rows:
            if abs(word["y"] - row[0]["y"]) < tolerance:
                row.append(word)
                placed = True
                break

        if not placed:
            rows.append([word])

    return rows


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

    if not word_list:
        st.error("No se extrajo texto.")
        return []

    # 🔥 CLUSTER REAL POR FILAS
    rows = cluster_rows(word_list)

    matches = []

    for row in rows:

        # Ordenar por eje X dentro de la fila
        row.sort(key=lambda w: w["x"])

        odds = [w["text"] for w in row if is_odd(w["text"])]

        if len(odds) < 3:
            continue

        odds = odds[:3]

        # Extraer palabras limpias
        words_only = []

        for w in row:
            if not is_odd(w["text"]):
                cleaned = clean_text(w["text"])
                if cleaned:
                    words_only.append(cleaned)

        if len(words_only) < 1:
            continue

        # Estrategia simple y estable:
        # Primer bloque alfabético = local
        # Último bloque alfabético = visitante
        home = words_only[0]
        away = words_only[-1] if len(words_only) > 1 else "Visitante"

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