import google.generativeai as genai
import streamlit as st
from PIL import Image
import json

def analyze_betting_image(uploaded_file):
    try:
        # Preparación de la imagen
        img = Image.open(uploaded_file)

        # Configuración segura
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)

        # ✅ USAMOS EL MODELO 2.0 (Corrije el Error 404)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = """
        Analiza esta captura de Caliente.mx NBA.
        Extrae los juegos y devuelve ÚNICAMENTE un JSON con esta estructura:
        {
          "juegos": [
            {
              "home": "equipo local",
              "away": "equipo visitante",
              "handicap": "valor",
              "total": "O/U valor",
              "moneyline": "momio"
            }
          ]
        }
        """

        response = model.generate_content([prompt, img])
        
        # Limpieza de la respuesta para asegurar JSON válido
        texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)

    except Exception as e:
        st.error(f"Vision AI error: {e}")
        return None
