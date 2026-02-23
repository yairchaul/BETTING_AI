import google.generativeai as genai
import streamlit as st
import PIL.Image
import json

def analyze_betting_image(uploaded_file):
    """
    Analiza la captura de pantalla de Caliente.mx usando Gemini Vision.
    """
    try:
        # 1. Configuración de API KEY desde Streamlit Secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)

        # 2. Inicialización del modelo con el nombre oficial para evitar errores 404
        # Usamos 'gemini-1.5-flash' que es la versión estable actual.
        model = genai.GenerativeModel('models/gemini-1.5-flash')

        # 3. Procesamiento de la imagen
        img = PIL.Image.open(uploaded_file)

        # 4. Prompt Maestro optimizado para evitar confusiones entre Hándicap y Totales
        prompt = """
        Actúa como analista profesional de apuestas NBA. Analiza la imagen de momios de Caliente.mx proporcionada.
        
        REGLAS DE EXTRACCIÓN:
        - EQUIPOS: Identifica el par de equipos (Local abajo, Visitante arriba).
        - HANDICAP: Son los números como +1.5 o -3 en la primera columna.
        - TOTALES: Son los números que acompañan a la 'O' (Over) o 'U' (Under). Ejemplo: 'O 232'.
        
        IMPORTANTE: Devuelve ÚNICAMENTE un objeto JSON válido, sin texto adicional, siguiendo esta estructura:
        {
          "juegos": [
            {
              "home": "Nombre Equipo Local",
              "away": "Nombre Equipo Visitante",
              "total_line": 232.5,
              "odds_over": -110
            }
          ]
        }
        """

        # 5. Generación de contenido
        response = model.generate_content([prompt, img])

        # 6. Limpieza profunda del texto recibido para asegurar un JSON puro
        clean_text = response.text
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0]
        
        data = json.loads(clean_text.strip())

        # Retornamos la lista de juegos para que main.py la procese
        return data.get("juegos", [])

    except Exception as e:
        # Error detallado para diagnóstico en el Dashboard
        st.error(f"Vision AI error: {str(e)}")
        return None
