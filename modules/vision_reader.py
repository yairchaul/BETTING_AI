import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import io


def get_vision_client():

    creds_dict = dict(st.secrets["google_credentials"])

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict
    )

    return vision.ImageAnnotatorClient(credentials=credentials)


def extract_teams(text):

    lines = text.split("\n")

    equipos = []

    for line in lines:

        line = line.strip()

        if len(line) < 3:
            continue

        # evitar momios y números
        if any(char.isdigit() for char in line):
            continue

        equipos.append(line)

    return equipos


def analyze_betting_image(image_file):

    client = get_vision_client()

    content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)

    text = response.text_annotations[0].description

    equipos = extract_teams(text)

    return equipos
