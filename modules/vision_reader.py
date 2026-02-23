import google.generativeai as genai
import streamlit as st
from PIL import Image
import json

def analyze_betting_image(uploaded_file):
    try:
        img = Image.open(uploaded_file)
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        # Buscar el mejor modelo disponible automáticamente
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Priorizar gemini-1.5-flash o gemini-2.0-flash si existen
        seleccionado = next((m for m in modelos if "flash" in m), modelos[0])
        
        model = genai.GenerativeModel(seleccionado)
        
        prompt = "Analiza y devuelve SOLO un JSON con la llave 'juegos' y los campos: home, away, handicap, total, moneyline."
        response = model.generate_content([prompt, img])
        
        texto = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(texto)
    except Exception as e:
        st.error(f"Error en Vision: {e}")
        return None
