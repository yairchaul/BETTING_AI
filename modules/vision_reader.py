# modules/vision_reader.py
import google.generativeai as genai
import streamlit as st
import PIL.Image
import json

def analyze_betting_image(uploaded_file):
    "Actúa como un experto analista de momios deportivos. Tu tarea es extraer los datos de la tabla de la NBA de Caliente.mx sin errores.

Reglas de Identificación Estrictas:

Equipos: Se encuentran en la columna central, uno arriba del otro (Local abajo, Visitante arriba).

Hándicap: Es la columna con valores como '+3', '-3', '+1.5'. Solo extrae el número, no el momio de al lado.

Totales (Over/Under): SIEMPRE comienzan con la letra 'O' (Over) o 'U' (Under). Ejemplo: 'O 232'.

Momios: Son los números con signo (+ o -) que están a la derecha de las líneas.

Instrucción de Salida: Devuelve un JSON con esta estructura exacta para cada juego detectado:
{
'juegos': [
{
'visitante': 'Nombre',
'local': 'Nombre',
'total_puntos': 'Solo el número del Over (ej. 232.5)',
'momio_over': 'Número (ej. -110)',
'handicap_local': 'Número (ej. -1.5)',
'momio_ganador_local': 'Número (ej. +100)'
}
]
}
Si un campo está vacío o bloqueado con un candado, pon null."
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
