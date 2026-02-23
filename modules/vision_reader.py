import google.generativeai as genai
import streamlit as st
from PIL import Image
import json

def analyze_betting_image(uploaded_file):
    try:
        img = Image.open(uploaded_file)
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)

        # --- AUTO-DETECCIÓN DE MODELO COMPATIBLE ---
        modelos_disponibles = [m.name for m in genai.list_models() 
                              if 'generateContent' in m.supported_generation_methods 
                              and 'vision' in m.name or 'flash' in m.name]
        
        # Elegimos el primero de la lista (el más actual que acepte visión)
        nombre_modelo = modelos_disponibles[0] if modelos_disponibles else "gemini-1.5-flash"
        model = genai.GenerativeModel(nombre_modelo)
        # --------------------------------------------

        prompt = """
        Analiza la imagen de Caliente.mx. Extrae los juegos en JSON puro:
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
        texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)

    except Exception as e:
        st.error(f"Fallo en detección automática: {e}")
        return None
