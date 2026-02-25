import google.generativeai as genai
from PIL import Image
import re
import streamlit as st

def analyze_betting_image(archivo):
    try:
        # Usamos tu secret configurado
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        img = Image.open(archivo)
        
        # MODELO ESTABLE: Eliminamos el sufijo -latest o versiones v1beta
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Extrae los datos de esta imagen de momios de forma estricta.
        Devuelve cada partido en una línea nueva con este formato:
        Equipo Local vs Equipo Visitante | L: [momio] | E: [momio] | V: [momio]
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
        return matches, f"✅ {len(matches)} partidos extraídos de la imagen."
    except Exception as e:
        return [], f"❌ Error de Motor: {str(e)}"
