from PIL import Image
import pytesseract
import cv2
import numpy as np
import re

# =============================
# PREPROCESS IMAGE (CLAVE)
# =============================

def preprocess_image(file):

    img = Image.open(file).convert("RGB")
    img = np.array(img)

    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Aumentar contraste
    gray = cv2.equalizeHist(gray)

    # Blur suave
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Threshold para limpiar fondo gris
    _, thresh = cv2.threshold(
        blur,
        150,
        255,
        cv2.THRESH_BINARY_INV
    )

    return thresh


# =============================
# EXTRAER EQUIPOS
# =============================

def extract_teams(text):

    lines = text.split("\n")

    equipos = []

    for line in lines:

        line = line.strip()

        # eliminar momios
        line = re.sub(r"[+-]\d+", "", line)

        # eliminar palabras basura
        if len(line) < 3:
            continue

        if "Empate" in line:
            continue

        # solo letras y espacios
        clean = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúñ ]", "", line)

        if len(clean.split()) >= 1:
            equipos.append(clean.strip())

    # eliminar duplicados
    equipos = list(dict.fromkeys(equipos))

    return equipos


# =============================
# MAIN OCR FUNCTION
# =============================

def analyze_betting_image(file):

    try:

        processed = preprocess_image(file)

        text = pytesseract.image_to_string(
            processed,
            config="--oem 3 --psm 6"
        )

        equipos = extract_teams(text)

        return equipos

    except Exception as e:
        print("OCR ERROR:", e)
        return []
