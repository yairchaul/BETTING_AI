import google.generativeai as genai
import streamlit as st
from PIL import Image # <-- Importante para corregir el error de Blob

def analyze_betting_image(uploaded_file):
    try:
        # Convertir el archivo subido de Streamlit a una imagen PIL
        img = Image.open(uploaded_file)
        
        # Configuración de la API
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Analiza esta imagen de Caliente.mx y extrae los juegos en este formato JSON exacto:
        [
          {
            "home": "Nombre Local",
            "away": "Nombre Visitante",
            "handicap": "valor y momio",
            "total": "O/U valor y momio",
            "moneyline": "momio"
          }
        ]
        Retorna solo el JSON puro.
        """

        # Enviar la imagen real convertida
        response = model.generate_content([prompt, img])
        return response.text.replace('```json', '').replace('```', '').strip()
        
    except Exception as e:
        return f"Error en Vision AI: {str(e)}"
