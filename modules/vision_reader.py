# modules/vision_reader.py
import google.generativeai as genai
import streamlit as st
import PIL.Image
import json

def analyze_betting_image(uploaded_file):
    """
    Usa Gemini Vision para extraer mercados de la captura de pantalla.
    """
    # Recuperamos la clave desde los secretos de Streamlit
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Configuración del modelo Vision
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Cargamos la imagen
    img = PIL.Image.open(uploaded_file)
    
    # Prompt Maestro para extracción de datos
    prompt = """
    Analiza esta imagen de una casa de apuestas (NBA). 
    Extrae los datos y devuélvelos ÚNICAMENTE en formato JSON puro.
    Estructura requerida por juego:
    {
      "juegos": [
        {
          "home": "Nombre equipo local",
          "away": "Nombre equipo visitante",
          "total_line": "Línea de Over/Under (ej. 232.5)",
          "odds_over": "Momio del Over (ej. -110)",
          "odds_under": "Momio del Under (ej. -110)",
          "moneyline_home": "Momio a ganar local",
          "moneyline_away": "Momio a ganar visitante"
        }
      ]
    }
    Si un dato no es visible, pon null.
    """
    
    try:
        response = model.generate_content([prompt, img])
        # Limpiamos la respuesta para obtener solo el JSON
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(raw_text)
    except Exception as e:
        st.error(f"Error en Vision AI: {e}")
        return None
