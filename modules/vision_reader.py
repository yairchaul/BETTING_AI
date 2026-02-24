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
# OCR ANALYSIS
# ============================

def analyze_betting_image(image_file):

    img = Image.open(image_file)

    text = pytesseract.image_to_string(
        img,
        lang="spa+eng"
    )

    # limpiar texto
    lines = text.split("\n")

    equipos = []

    for line in lines:
        line = line.strip()

        if "vs" in line.lower():
            parts = re.split(r"vs|VS|Vs", line)
            equipos.extend([p.strip() for p in parts])

    return equipos
