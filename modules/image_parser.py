# modules/image_parser.py
import re
import streamlit as st
from PIL import Image
import pytesseract
import easyocr

class ImageParser:
    def __init__(self):
        # Inicializar EasyOCR como respaldo
        self.reader = easyocr.Reader(['es', 'en'], gpu=False)
    
    def extract_matches_from_text(self, text):
        """Extrae partidos del formato específico de tu imagen"""
        lines = text.split('\n')
        matches = []
        current_league = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detectar liga (líneas con guiones o formato especial)
            if ' - ' in line and len(line.split(' - ')) >= 2:
                current_league = line
            
            # Detectar partido (dos equipos separados por vs o similar)
            elif ' vs ' in line.lower() or '\n' and i+1 < len(lines):
                # Podría ser formato de dos líneas
                if ' vs ' in line.lower():
                    parts = re.split(r'\s+vs\s+', line, flags=re.IGNORECASE)
                    if len(parts) == 2:
                        matches.append({
                            'local': parts[0].strip(),
                            'visitante': parts[1].strip(),
                            'liga': current_league
                        })
                else:
                    # Formato de dos líneas: equipo1 \n equipo2
                    local = line
                    visitante = lines[i+1].strip() if i+1 < len(lines) else ''
                    if local and visitante and not any(x in local for x in ['Score', 'Points']):
                        matches.append({
                            'local': local,
                            'visitante': visitante,
                            'liga': current_league
                        })
                        i += 1  # Saltar la siguiente línea
            
            i += 1
        
        return matches
    
    def parse_image(self, uploaded_file):
        """Procesa la imagen y extrae los partidos"""
        try:
            # Leer con EasyOCR (más robusto para diferentes formatos)
            image = Image.open(uploaded_file)
            result = self.reader.readtext(np.array(image))
            
            full_text = ' '.join([item[1] for item in result])
            
            # Debug
            st.text("Texto detectado:")
            st.text(full_text[:500])
            
            # Extraer partidos
            matches = self.extract_matches_from_text(full_text)
            
            return matches, full_text
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return [], ""