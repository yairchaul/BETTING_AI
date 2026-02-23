import google.generativeai as genai
import streamlit as st
import PIL.Image
import json

def analyze_betting_image(uploaded_file):
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    img = PIL.Image.open(uploaded_file)
    
    # PROMPT MAESTRO ANTI-CONFUSIÓN
    prompt = """
    Analiza esta imagen de momios de la NBA. 
    REGLA ORO: NO confundas 'Hándicap' con 'Totales'. 
    - El Hándicap son números como +1.5, -3, etc.
    - Los Totales SIEMPRE llevan una 'O' (Over) o 'U' (Under) antes del número (ej. O 232).
    
    Extrae los datos en este formato JSON:
    {
      "juegos": [
        {
          "home": "equipo local",
          "away": "equipo visitante",
          "total_line": "número tras la O o U",
          "odds_over": "momio a la derecha de la O",
          "handicap_home": "valor de la columna hándicap"
        }
      ]
    }
    """
    
    try:
        response = model.generate_content([prompt, img])
        return json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except:
        return None
