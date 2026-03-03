import re
import streamlit as st
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser

class UniversalParser:
    """
    Parser universal que orquestra Google Vision, Groq Vision y 
    lógica de Regex para una extracción infalible.
    """
    
    def __init__(self):
        self.forbidden_words = ['empate', 'empaté', 'draw', 'vs', 'v', 'local', 'visitante', 'cuota', 'odds']
        self.google_parser = ImageParser()
        self.groq_parser = GroqVisionParser()
    
    def parse_image(self, image_bytes):
        """
        Método principal que combina todas las estrategias.
        """
        all_matches = []

        # ESTRATEGIA 1: Google Vision (Precisión por coordenadas)
        # Este usa la lógica de píxeles que ya corregimos para nombres compuestos
        with st.spinner("Analizando estructura visual..."):
            google_results = self.google_parser.process_image(image_bytes)
            if google_results:
                all_matches.extend(google_results)

        # ESTRATEGIA 2: Groq Vision (Razonamiento Semántico)
        # Si Google falló o detectó poco, Groq entra como refuerzo
        if len(all_matches) < 2 and self.groq_parser.is_available:
            with st.spinner("Refinando con IA visual..."):
                groq_results = self.groq_parser.extract_matches_with_vision(image_bytes)
                if groq_results:
                    all_matches.extend(groq_results)

        # ESTRATEGIA 3: Fallback de Texto Puro (Tu lógica original de Regex)
        # Solo si lo anterior no dio resultados
        if len(all_matches) == 0:
            # Extraemos texto plano de la respuesta de Google para usar tu parse() original
            from google.cloud import vision
            client = self.google_parser.client
            if client:
                image = vision.Image(content=image_bytes)
                response = client.text_detection(image=image)
                text_content = response.text_annotations[0].description if response.text_annotations else ""
                all_matches.extend(self.parse(text_content))

        return self._deduplicate(all_matches)

    def _deduplicate(self, matches):
        """Elimina duplicados basados en nombres de equipos"""
        unique_matches = []
        seen = set()
        for m in matches:
            # Normalizamos para comparar: "Santos Laguna" == "SANTOS LAGUNA"
            key = (m.get('home', '').strip().upper(), m.get('away', '').strip().upper())
            if key not in seen and m.get('home') and m.get('away'):
                seen.add(key)
                unique_matches.append(m)
        return unique_matches

    # --- Mantenemos tu lógica original de procesamiento de texto intacta ---

    def _preprocess_lines(self, lines):
        processed_lines = []
        for line in lines:
            match = re.match(r'^([+-]\d{3,4})\s+(Empate.*?)$', line, re.IGNORECASE)
            if match:
                processed_lines.append(match.group(1))
                processed_lines.append(match.group(2))
            else:
                processed_lines.append(line)
        return processed_lines
    
    def parse(self, text):
        """Lógica original de parseo por líneas de texto"""
        raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
        lines = self._preprocess_lines(raw_lines)
        
        matches = []
        # Estrategia de 6 líneas
        matches.extend(self._parse_six_line_format(lines))
        
        # Estrategia de 1 línea
        if len(matches) == 0:
            matches.extend(self._parse_one_line_format(lines))
        
        return matches
    
    def _parse_six_line_format(self, lines):
        matches = []
        i = 0
        while i < len(lines) - 5:
            home, home_odd = lines[i], lines[i+1]
            empate_word, empate_odd = lines[i+2], lines[i+3]
            away, away_odd = lines[i+4], lines[i+5]
            
            if 'empate' in empate_word.lower():
                if (re.match(r'^[+-]\d+$', home_odd) and
                    re.match(r'^[+-]\d+$', empate_odd) and
                    re.match(r'^[+-]\d+$', away_odd)):
                    
                    home_clean = re.sub(r'[|•\-_=+*]', '', home).strip()
                    away_clean = re.sub(r'[|•\-_=+*]', '', away).strip()
                    
                    if (home_clean.lower() not in self.forbidden_words and 
                        away_clean.lower() not in self.forbidden_words and
                        len(home_clean) > 2 and len(away_clean) > 2):
                        
                        matches.append({
                            'home': home_clean,
                            'away': away_clean,
                            'all_odds': [home_odd, empate_odd, away_odd]
                        })
                        i += 6
                        continue
            i += 1
        return matches
    
    def _parse_one_line_format(self, lines):
        matches = []
        pattern = r'^(.+?)\s+([+-]\d{3,4})\s+([Ee]mpat[ea]?)\s+([+-]\d{3,4})\s+(.+?)\s+([+-]\d{3,4})$'
        for line in lines:
            match = re.match(pattern, line)
            if match:
                home_clean = re.sub(r'[|•\-_=+*]', '', match.group(1)).strip()
                away_clean = re.sub(r'[|•\-_=+*]', '', match.group(5)).strip()
                if (home_clean.lower() not in self.forbidden_words and 
                    away_clean.lower() not in self.forbidden_words):
                    matches.append({
                        'home': home_clean,
                        'away': away_clean,
                        'all_odds': [match.group(2), match.group(4), match.group(6)]
                    })
        return matches
