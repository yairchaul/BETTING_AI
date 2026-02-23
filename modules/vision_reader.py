import google.generativeai as genai
import streamlit as st
import PIL.Image
import json


def analyze_betting_image(uploaded_file):

    # API KEY desde Streamlit Secrets
    api_key = st.secrets["GEMINI_API_KEY"]

    genai.configure(api_key=api_key)

    # ✅ MODELO ACTUAL
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    img = PIL.Image.open(uploaded_file)

    prompt = """
    Actúa como analista profesional de apuestas NBA.

    Analiza la imagen de momios.

    REGLAS:
    - Handicap = +1.5 / -3
    - Totales = O 232 o U 232
    - Ignora spreads cuando leas Totales.

    Devuelve SOLO JSON válido:

    {
      "juegos":[
        {
          "home":"equipo local",
          "away":"equipo visitante",
          "total_line":232,
          "odds_over":-110
        }
      ]
    }
    """

    try:

        response = model.generate_content([prompt, img])

        clean_text = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(clean_text)

        return data["juegos"]

    except Exception as e:

        st.error(f"Vision AI error: {e}")
        return None
