import google.generativeai as genai
from PIL import Image
import re

def analyze_betting_image(archivo):
    try:
        img = Image.open(archivo)
        # Ajuste de modelo para evitar Error 404
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        prompt = """
        Analiza esta imagen de momios. Extrae cada partido y sus cuotas.
        Formato de salida: Local vs Visitante | L: [momio] | E: [momio] | V: [momio]
        No incluyas introducciones, solo los datos.
        """
        response = model.generate_content([prompt, img])
        raw_text = response.text

        # Tu patrón de extracción global favorito
        pattern_teams = r'([A-Z][a-zñáéíóú]+(?:\s[A-Z][a-zñáéíóú]+)*)'
        pattern_odds = r'([+-]\d{2,4})'

        teams = re.findall(pattern_teams, raw_text)
        odds = re.findall(pattern_odds, raw_text)

        matches = []
        for i in range(0, len(teams) - 1, 2):
            idx_o = (i // 2) * 3
            if idx_o + 2 < len(odds):
                matches.append({
                    "home": teams[i].strip(), "away": teams[i+1].strip(),
                    "home_odd": odds[idx_o], "draw_odd": odds[idx_o+1], "away_odd": odds[idx_o+2]
                })
        
        return matches, f"✅ {len(matches)} partidos detectados correctamente."
    except Exception as e:
        return [], f"❌ Error de Motor: {str(e)}"
