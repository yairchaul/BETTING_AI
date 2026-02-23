import google.generativeai as genai
import streamlit as st
import PIL.Image
import json

def analyze_betting_image(uploaded_file):

    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.0-flash")

    image = PIL.Image.open(uploaded_file)

    prompt = """
    Actúa como analista profesional de apuestas deportivas.

    Analiza esta captura de apuestas NBA de Caliente.mx.

    REGLAS IMPORTANTES:
    - Handicap = números +1.5, -3, etc.
    - Totales siempre tienen O (Over) o U (Under).
    - NO confundas columnas.

    Devuelve SOLO JSON válido:

    {
      "juegos":[
        {
          "away":"equipo visitante",
          "home":"equipo local",
          "total_line":number,
          "odds_over":number,
          "handicap_home":number
        }
      ]
    }
    """

    try:
        response = model.generate_content([prompt, image])

        clean = (
            response.text
            .replace("```json","")
            .replace("```","")
            .strip()
        )

        return json.loads(clean)

    except Exception as e:
        st.error(f"Vision AI error: {e}")
        return None
st.write("KEY LOADED:", "GEMINI_API_KEY" in st.secrets)
