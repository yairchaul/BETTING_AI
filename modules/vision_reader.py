import pytesseract
from PIL import Image


def analyze_betting_image(image_file):
    """
    Lee la imagen y detecta nombres de equipos automáticamente.
    """

    img = Image.open(image_file)

    text = pytesseract.image_to_string(img)

    lines = text.split("\n")

    equipos = []

    for line in lines:

        line = line.strip()

        if len(line) > 3 and not any(char.isdigit() for char in line):
            equipos.append(line)

    # limpiar duplicados
    equipos = list(dict.fromkeys(equipos))

    return equipos
