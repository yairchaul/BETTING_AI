import re
from PIL import Image
import pytesseract # O el motor de visión que estés usando (Gemini Vision/Google OCR)

def analyze_betting_image(archivo):
    """
    Lee la imagen real subida por el usuario y extrae equipos y momios globalmente.
    """
    try:
        # 1. Convertir el archivo subido a una imagen procesable
        img = Image.open(archivo)
        
        # 2. Extraer texto real de la imagen (OCR)
        # Si usas la API de Gemini Vision, aquí iría la llamada a la API.
        raw_text = pytesseract.image_to_string(img) 
        
        # 3. Limpieza de ruido del OCR
        raw_text = raw_text.replace('\n', ' ')

        # Patrones Globales (Inamovibles)
        pattern_teams = r'([A-Z][a-zñáéíóú]+(?:\s[A-Z][a-zñáéíóúFCUnite]+)*)'
        pattern_odds = r'([+-]\d{2,4})'

        teams = re.findall(pattern_teams, raw_text)
        odds = re.findall(pattern_odds, raw_text)

        matches = []
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
            return [], "⚠️ No se detectaron equipos o momios claros. Revisa la nitidez de la imagen."
            
        return matches, f"✅ Éxito: {len(matches)} partidos analizados de tu imagen."

    except Exception as e:
        return [], f"❌ Error al procesar la imagen: {str(e)}"
