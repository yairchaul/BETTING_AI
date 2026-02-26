from google.cloud import vision
import streamlit as st
import re


# =============================
# CLIENTE GOOGLE VISION
# =============================
def get_vision_client():
    creds_dict = dict(st.secrets["google_credentials"])
    return vision.ImageAnnotatorClient.from_service_account_info(creds_dict)


# =============================
# VALIDADORES
# =============================
def is_odd(text):
    return re.match(r"^(\+|\-)?\d+(\.\d+)?$", text)


def is_draw(text):
    return "empate" in text.lower()


# =============================
# ANALISIS PRINCIPAL
# =============================
def analyze_betting_image(uploaded_file):

    client = get_vision_client()

    content = uploaded_file.read()
    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)

    elements = []

    # =============================
    # EXTRAER TEXTO + POSICION
    # =============================
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:

                text = "".join(
                    ["".join([s.text for s in w.symbols])
                     for w in paragraph.words]
                )

                vertices = paragraph.bounding_box.vertices

                x_center = sum(v.x for v in vertices) / 4
                y_center = sum(v.y for v in vertices) / 4

                elements.append({
                    "text": text.strip(),
                    "x": x_center,
                    "y": y_center
                })

    if not elements:
        return []

    # =============================
    # ORDENAR POR ALTURA
    # =============================
    elements.sort(key=lambda e: e["y"])

    # =============================
    # AGRUPAR FILAS VISUALES
    # =============================
    ROW_THRESHOLD = 35

    rows = []
    current_row = [elements[0]]

    for el in elements[1:]:

        if abs(el["y"] - current_row[-1]["y"]) < ROW_THRESHOLD:
            current_row.append(el)
        else:
            rows.append(current_row)
            current_row = [el]

    rows.append(current_row)

    partidos = []

    # =============================
    # INTERPRETAR CADA FILA COMO TABLA
    # =============================
    for row in rows:

        # ordenar columnas
        row.sort(key=lambda r: r["x"])

        textos = [r["text"] for r in row]

        # limpiar ruido
        textos = [t for t in textos if len(t) > 2]

        # buscamos patrón:
        # equipo A ... empate ... equipo B
        equipo_a = None
        equipo_b = None

        for i, t in enumerate(textos):

            if is_draw(t):
                if i > 0 and i < len(textos) - 1:
                    equipo_a = textos[i - 1]
                    equipo_b = textos[i + 1]
                    break

        if equipo_a and equipo_b:

            partidos.append(equipo_a)
            partidos.append(equipo_b)

    # quitar duplicados manteniendo orden
    partidos = list(dict.fromkeys(partidos))

    return partidos
