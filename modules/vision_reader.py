import google.generativeai as genai
from PIL import Image
import streamlit as st
import json

# --- CONFIG GEMINI ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")


def analyze_betting_image(uploaded_file):

    image = Image.open(uploaded_file)

    prompt = """
    Read this NBA betting screenshot.

    Extract ALL games visible.

    Return ONLY valid JSON:

    [
        {
            "home":"",
            "away":"",
            "spread":"",
            "total":"",
            "odds_home":"",
            "odds_away":""
        }
    ]

    No explanation.
    JSON only.
    """

    response = model.generate_content([prompt, image])

    text = response.text.strip()

    # Limpieza automática Gemini
    text = text.replace("```json", "").replace("```", "")

    try:
        return json.loads(text)
    except Exception:
        st.error("Gemini no devolvió JSON válido")
        return []
