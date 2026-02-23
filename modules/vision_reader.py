import google.generativeai as genai
import streamlit as st
from PIL import Image
import json


def analyze_betting_image(uploaded_file):

    try:
        # -------------------------
        # Imagen
        # -------------------------
        img = Image.open(uploaded_file)

        # -------------------------
        # API KEY
        # -------------------------
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)

        # ✅ MODELO ACTUAL
        model = genai.GenerativeModel("gemini-2.0-flash")

        # -------------------------
        # PROMPT PROFESIONAL
        # -------------------------
        prompt = """
        Actúa como analista profesional de apuestas deportivas.

        Analiza esta captura de Caliente.mx NBA.

        REGLAS:
        - Handicap = +1.5, -3, etc.
        - Totales siempre contienen O o U.
        - No mezclar columnas.

        Devuelve SOLO JSON válido:

        {
          "juegos":[
            {
              "home":"equipo local",
              "away":"equipo visitante",
              "total_line":number,
              "odds_over":number,
              "handicap_home":number
            }
          ]
        }
        """

        response = model.generate_content([prompt, img])

        clean = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(clean)

    except Exception as e:
        st.error(f"Vision AI error: {e}")
        return None
