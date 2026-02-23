import google.generativeai as genai
import streamlit as st
from PIL import Image

def analyze_betting_image(image):
    """
    Analiza una captura de pantalla de Caliente.mx usando Gemini 1.5 Flash.
    """
    # 1. Configurar la API Key desde los Secrets de Streamlit
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    # 2. Inicializar el modelo estable 1.5 Flash
    # Usamos este porque el 2.0-flash dio error de disponibilidad
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = """
    Analiza esta imagen de apuestas deportivas y extrae los datos en formato JSON.
    Para cada partido, necesito:
    - equipo_local
    - equipo_visitante
    - handicap (puntos y momio)
    - total_puntos (O/U y momio)
    - moneyline (momios de ambos)
    Retorna solo el JSON puro.
    """

    try:
        # 3. Generar contenido con la imagen
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error en Vision AI: {str(e)}"
