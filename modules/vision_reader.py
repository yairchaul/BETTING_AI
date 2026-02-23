import streamlit as st
from google import genai
from PIL import Image
import json


def analyze_betting_image(uploaded_file):

    try:
        # ✅ API KEY desde Streamlit Secrets
        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )

        img = Image.open(uploaded_file)

        prompt = """
        Actúa como analista profesional NBA betting.

        Analiza la imagen de momios.

        REGLAS IMPORTANTES:
        - Handicap = +1.5 / -3
        - Totales siempre empiezan con O o U
        - Ignora columnas irrelevantes.

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

        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=[prompt, img],
        )

        clean = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(clean)

        return data["juegos"]

    except Exception as e:
        st.error(f"Vision AI error: {e}")
        return None
