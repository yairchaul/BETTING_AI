import google.generativeai as genai
from PIL import Image
import re

def analyze_betting_image(archivo):
    """
    Usa Gemini Vision para leer la imagen y extraer equipos y momios de forma global.
    """
    try:
        img = Image.open(archivo)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Analiza esta imagen de apuestas y extrae TODOS los partidos.
        Para cada partido busca: Nombre Equipo Local, Nombre Equipo Visitante, Momio Local, Momio Empate, Momio Visitante.
        Devuelve solo el texto en este formato:
        Local vs Visitante | L: momio | E: momio | V: momio
        """
        
        response = model.generate_content([prompt, img])
        texto = response.text
        
        # Procesamiento del texto extraído para convertirlo en lista de diccionarios
        matches = []
        lineas = texto.strip().split('\n')
        for linea in lineas:
            # RegEx para capturar equipos y momios del formato de respuesta
            res = re.search(r"(.+?) vs (.+?) \| L: (.+?) \| E: (.+?) \| V: (.+?)", linea)
            if res:
                matches.append({
                    "home": res.group(1).strip(),
                    "away": res.group(2).strip(),
                    "home_odd": res.group(3).strip(),
                    "draw_odd": res.group(4).strip(),
                    "away_odd": res.group(5).strip()
                })
        
        return matches, "Lectura de Vision AI completada."
    except Exception as e:
        return [], f"Error en Vision: {str(e)}"
