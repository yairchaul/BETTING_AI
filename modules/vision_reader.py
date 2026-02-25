import google.generativeai as genai
from PIL import Image
import re
import streamlit as st

def analyze_betting_image(archivo):
    try:
        # Configuración con Secrets
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        img = Image.open(archivo)
        
        # Cambiamos a 'gemini-1.5-flash' sin sufijos beta para evitar el 404
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Extrae los datos de esta imagen de momios. 
        Formato requerido: Local vs Visitante | L: [momio] | E: [momio] | V: [momio]
        Ignora logos y céntrate en el texto y números.
        """
        response = model.generate_content([prompt, img])
        raw_text = response.text

        # Tu lógica de extracción global
        pattern_teams = r'([A-Z][a-zñáéíóú]+(?:\s[A-Z][a-zñáéíóú]+)*)'
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
        return matches, f"✅ Éxito: {len(matches)} partidos analizados."
    except Exception as e:
        return [], f"❌ Error de Motor: {str(e)}"
