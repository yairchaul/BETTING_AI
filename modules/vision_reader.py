import google.generativeai as genai
import streamlit as st

def analyze_betting_image(image):
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Ajustamos las llaves a 'home' y 'away' para que main.py no falle
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
    Retorna solo el JSON, sin texto adicional.
    """

    try:
        response = model.generate_content([prompt, image])
        # Limpiamos el texto por si la IA agrega comillas de bloque
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json_text
    except Exception as e:
        return f"Error: {str(e)}"
