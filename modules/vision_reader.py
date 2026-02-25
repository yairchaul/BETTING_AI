import google.generativeai as genai
from PIL import Image
import re
import streamlit as st

def analyze_betting_image(archivo):
    """
    Motor de Visión Original: Lee la imagen real y extrae datos globales.
    """
    try:
        img = Image.open(archivo)
        # Usamos la versión estable del modelo para evitar el error 404
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        prompt = """
        Extrae los datos de esta imagen de apuestas. Para cada partido detectado, 
        devuelve EXACTAMENTE una línea con este formato:
        Local vs Visitante | L: momio | E: momio | V: momio
        No añadidas texto extra, solo los partidos encontrados.
        """
        
        response = model.generate_content([prompt, img])
        texto_sucio = response.text
        
        matches = []
        # Procesamos línea por línea el resultado de la IA
        for linea in texto_sucio.strip().split('\n'):
            res = re.search(r"(.+?) vs (.+?) \| L: (.+?) \| E: (.+?) \| V: (.+?)", linea)
            if res:
                matches.append({
                    "home": res.group(1).strip(),
                    "away": res.group(2).strip(),
                    "home_odd": res.group(3).strip(),
                    "draw_odd": res.group(4).strip(),
                    "away_odd": res.group(5).strip()
                })
        
        if not matches:
            return [], "No se pudieron estructurar los datos de la imagen."
            
        return matches, f"✅ Se detectaron {len(matches)} partidos en tu imagen."

    except Exception as e:
        return [], f"⚠️ Error Crítico en Motor de Visión: {str(e)}"
