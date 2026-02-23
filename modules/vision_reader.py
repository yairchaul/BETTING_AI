import google.generativeai as genai
import streamlit as st
from PIL import Image # <-- Librería necesaria para convertir la imagen

def analyze_betting_image(uploaded_file):
    try:
        # 1. Convertir el archivo de Streamlit a una imagen real
        img = Image.open(uploaded_file)
        
        # 2. Configuración de la API Key segura
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 3. Usar el modelo correcto (gemini-1.5-flash)
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
        Retorna solo el JSON puro, sin texto adicional.
        """

        # 4. Enviar la imagen ya procesada
        response = model.generate_content([prompt, img])
        return response.text.replace('```json', '').replace('```', '').strip()
        
    except Exception as e:
        return f"Error en Vision AI: {str(e)}"
