import google.generativeai as genai
import streamlit as st
from PIL import Image

def analyze_betting_image(uploaded_file):
    try:
        # Convertir archivo de Streamlit a imagen PIL
        img = Image.open(uploaded_file)
        
        # Configuración de API
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # CAMBIO CLAVE: Usamos solo 'gemini-1.5-flash' sin rutas adicionales
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Extrae los datos de esta imagen de Caliente.mx en formato JSON puro:
        [
          {
            "home": "Local",
            "away": "Visitante",
            "handicap": "valor y momio",
            "total": "O/U valor y momio",
            "moneyline": "momio"
          }
        ]
        """

        # Generar contenido
        response = model.generate_content([prompt, img])
        
        # Limpiar respuesta
        return response.text.replace('```json', '').replace('```', '').strip()
        
    except Exception as e:
        # Esto nos dirá exactamente qué falla si el error persiste
        return f"Error detallado: {str(e)}"
