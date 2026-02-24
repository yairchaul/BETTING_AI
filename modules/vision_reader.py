import pytesseract
from PIL import Image
import platform
import re

# ============================
# FIX STREAMLIT CLOUD
# ============================

if platform.system() == "Linux":
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ============================
# LIMPIEZA TEXTO OCR
# ============================

def clean_line(line):

    line = line.strip()

    # quitar momios +120 -150 etc
    line = re.sub(r"[+-]\d+", "", line)

    # quitar números sueltos
    line = re.sub(r"\d+", "", line)

    return line.strip()


# ============================
# DETECTOR PARTIDOS
# ============================

def analyze_betting_image(image_file):

    img = Image.open(image_file)

    text = pytesseract.image_to_string(
        img,
        lang="spa+eng"
    )

    lines = text.split("\n")

    posibles_equipos = []

    for line in lines:

        line = clean_line(line)

        if len(line) > 3 and "empate" not in line.lower():
            posibles_equipos.append(line)

    # eliminar duplicados
    equipos = list(dict.fromkeys(posibles_equipos))

    return equipos
