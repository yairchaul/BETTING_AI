import pytesseract
from PIL import Image
import re
import streamlit as st

class TesseractParser:
    def __init__(self):
        # Configurar ruta de Tesseract (ajustar según instalación)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def parse_image(self, image_bytes):
        """Extrae texto de imagen usando Tesseract"""
        try:
            image = Image.open(image_bytes)
            text = pytesseract.image_to_string(image, lang='spa')
            return self._parse_text(text)
        except Exception as e:
            st.error(f"Error en OCR: {e}")
            return []
    
    def _parse_text(self, text):
        """Convierte texto a estructura de partidos"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        matches = []
        i = 0
        while i < len(lines):
            try:
                if i + 4 < len(lines):
                    local = lines[i]
                    cuota_local = lines[i+1]
                    empate = lines[i+2]
                    cuota_empate = lines[i+3]
                    visitante = lines[i+4]
                    cuota_visitante = lines[i+5] if i+5 < len(lines) else ''
                    
                    # Verificar que tiene pinta de partido
                    if any(c in cuota_local for c in ['+', '-']) and \
                       any(c in cuota_visitante for c in ['+', '-']):
                        matches.append({
                            'local': local,
                            'cuota_local': cuota_local,
                            'empate': empate,
                            'cuota_empate': cuota_empate,
                            'visitante': visitante,
                            'cuota_visitante': cuota_visitante
                        })
                        i += 6
                    else:
                        i += 1
                else:
                    i += 1
            except:
                i += 1
        
        return matches
