import google.generativeai as genai
import streamlit as st
from PIL import Image # <-- Fundamental para corregir el error de Blob

def analyze_betting_image(uploaded_file):
    try:
        # 1. Convertir el archivo subido en una imagen que la IA entienda
        img = Image.open(uploaded_file)
        
        # 2. Configuración
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Analiza esta imagen de Caliente.mx. Extrae los juegos en este formato JSON exacto:
        [
          {
            "home": "Nombre Equipo Local",
            "away": "Nombre Equipo Visitante",
            "handicap": "valor y momio",
            "total": "O/U valor y momio",
            "moneyline": "momio"
          }
        ]
        Retorna solo el JSON puro, sin explicaciones.
        """

        # 3. Llamada a la IA pasando la imagen convertida
        response = model.generate_content([prompt, img])
        return response.text.replace('```json', '').replace('```', '').strip()
        
    except Exception as e:
        return f"Error en Vision AI: {str(e)}"
