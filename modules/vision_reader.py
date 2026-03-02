import pytesseract
import cv2
import re
import numpy as np


# -----------------------------
# PREPROCESAMIENTO DE IMAGEN
# -----------------------------
def preprocess_image(image_path):

    img = cv2.imread(image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # mejora contraste
    gray = cv2.equalizeHist(gray)

    # quitar ruido
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # binarizar
    _, thresh = cv2.threshold(
        gray, 150, 255, cv2.THRESH_BINARY_INV
    )

    return thresh


# -----------------------------
# OCR
# -----------------------------
def extract_text(image_path):

    img = preprocess_image(image_path)

    config = "--psm 6"

    text = pytesseract.image_to_string(img, config=config)

    return text


# -----------------------------
# PARSER PRINCIPAL
# -----------------------------
def parse_matches(text):

    lines = [
        l.strip()
        for l in text.split("\n")
        if l.strip() != ""
    ]

    games = []

    i = 0

    while i < len(lines) - 2:

        # buscamos patrón:
        # Equipo + cuota
        # Empate + cuota
        # Equipo + cuota

        try:

            home_line = lines[i]
            draw_line = lines[i + 1]
            away_line = lines[i + 2]

            if "Empate" not in draw_line:
                i += 1
                continue

            home_team, home_odd = extract_team_odd(home_line)
            _, draw_odd = extract_team_odd(draw_line)
            away_team, away_odd = extract_team_odd(away_line)

            games.append({
                "home_team": home_team,
                "away_team": away_team,
                "home_odd": home_odd,
                "draw_odd": draw_odd,
                "away_odd": away_odd
            })

            i += 3

        except:
            i += 1

    return games


# -----------------------------
# EXTRAER EQUIPO + CUOTA
# -----------------------------
def extract_team_odd(line):

    match = re.search(r"(.+?)\s*([+-]\d+)", line)

    if not match:
        return line, None

    team = match.group(1).strip()
    odd = int(match.group(2))

    return team, odd


# -----------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------
def analyze_betting_image(image_path):

    text = extract_text(image_path)

    games = parse_matches(text)

    return games
