from google.cloud import vision
import streamlit as st
import re


def get_vision_client():

    creds_dict = dict(st.secrets["google_credentials"])

    return vision.ImageAnnotatorClient.from_service_account_info(
        creds_dict
    )


def extract_teams(text):

    lines = text.split("\n")

    equipos = []

    for line in lines:

        line = line.strip()

        # limpiar momios
        clean = re.sub(r'[\+\-\d\.]+', '', line)

        # ignorar ruido
        if len(clean) > 4 and "Empate" not in clean:
            equipos.append(clean)

    # eliminar duplicados
    equipos = list(dict.fromkeys(equipos))

    return equipos


def analyze_betting_image(uploaded_file):

    client = get_vision_client()

    content = uploaded_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)

    text = response.text_annotations[0].description

    equipos = extract_teams(text)

    return equipos
