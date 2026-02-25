import google.generativeai as genai
from PIL import Image
import re

def analyze_betting_image(archivo):
    """
    EXTRACCIÓN GLOBAL REAL: Lee tu imagen y usa RegEx para estructurar los datos.
    """
    try:
        # 1. Cargar la imagen real subida
        img = Image.open(archivo)
        
        # Usamos el modelo flash más reciente y estable
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 2. Pedimos a la IA que extraiga el texto bruto de forma limpia
        prompt = "Extrae todos los nombres de equipos y momios de esta imagen. No expliques nada, solo dame el texto."
        response = model.generate_content([prompt, img])
        raw_text = response.text

        # 3. Tu lógica de Patrones (La que te funcionaba)
        # Captura equipos (Mayúsculas compuestas)
        pattern_teams = r'([A-Z][a-zñáéíóú]+(?:\s[A-Z][a-zñáéíóú]+)*)'
        # Captura momios americanos (+/-)
        pattern_odds = r'([+-]\d{2,4})'

        teams = re.findall(pattern_teams, raw_text)
        odds = re.findall(pattern_odds, raw_text)

        matches = []
        # Vinculación lógica: Cada 2 equipos, 3 momios
        for i in range(0, len(teams) - 1, 2):
            idx_o = (i // 2) * 3
            if idx_o + 2 < len(odds):
                matches.append({
                    "home": teams[i].strip(),
                    "away": teams[i+1].strip(),
                    "home_odd": odds[idx_o],
                    "draw_odd": odds[idx_o+1],
                    "away_odd": odds[idx_o+2]
                })
        
        if not matches:
            return [], "⚠️ El OCR no encontró datos claros en esta captura."
            
        return matches, f"✅ Global: {len(matches)} partidos identificados en tu imagen."

    except Exception as e:
        # Si hay error de API (como el 404 que te salió), lo atrapamos aquí
        return [], f"❌ Error de conexión con el Motor: {str(e)}"
