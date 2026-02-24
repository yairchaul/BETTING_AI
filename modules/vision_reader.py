import cv2
import numpy as np
import pytesseract
from PIL import Image
import re


def preprocess_image(file):

    img = Image.open(file).convert("RGB")
    img = np.array(img)

    # Escalar imagen (CRÍTICO)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aumentar contraste
    gray = cv2.equalizeHist(gray)

    # Blur ligero
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold fuerte
    _, thresh = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return thresh


def extract_teams(text):

    lines = text.split("\n")

    equipos = []

    for line in lines:

        line = line.strip()

        # quitar números y momios
        clean = re.sub(r'[\+\-\d\.]+', '', line)

        # solo palabras largas (equipos)
        if len(clean.split()) >= 1 and len(clean) > 3:
            if not any(char.isdigit() for char in clean):
                equipos.append(clean)

    # eliminar duplicados
    equipos = list(dict.fromkeys(equipos))

    return equipos


def analyze_betting_image(file):

    processed = preprocess_image(file)

    text = pytesseract.image_to_string(
        processed,
        config="--psm 6"
    )

    equipos = extract_teams(text)

    return equipos
