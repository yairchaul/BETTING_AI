import google.generativeai as genai
from PIL import Image
import streamlit as st
import json

# Lee API key desde Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")


def analyze_betting_image(image_file):

    img = Image.open(image_file)

    prompt = """
    Analiza esta imagen de apuestas NBA.

    Extrae TODOS los partidos visibles.

    Devuelve SOLO JSON con este formato:

    [
        {
            "home": "",
            "away": "",
            "spread": "",
            "total": "",
            "odds_home": "",
            "odds_away": ""
        }
    ]

    NO expliques nada.
    SOLO JSON.
    """

    response = model.generate_content([prompt, img])

    text = response.text.strip()

    try:
        data = json.loads(text)
        return data
    except:
        return []
