import google.generativeai as genai
import streamlit as st
import json

def analyze_betting_image(image):
    # Configuración de API con tu llave de Nivel 1 activa
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # El prompt ahora exige las llaves exactas: 'home', 'away', etc.
    prompt = """
    Analiza esta imagen de Caliente.mx y extrae los juegos en este formato JSON exacto:
    [
      {
        "home": "Nombre Equipo Local",
        "away": "Nombre Equipo Visitante",
        "handicap": "valor y momio",
        "total": "O/U valor y momio",
        "moneyline": "momio"
      }
    ]
    Importante: No inventes datos, si no los ves pon 'N/A'. Retorna solo JSON puro.
    """

    try:
        response = model.generate_content([prompt, image])
        # Limpieza de formato para asegurar que sea JSON válido
        texto_limpio = response.text.replace('```json', '').replace('```', '').strip()
        return texto_limpio
    except Exception as e:
        return f"Error en Vision AI: {str(e)}"
