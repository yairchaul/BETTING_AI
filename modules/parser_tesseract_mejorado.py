import pytesseract
from PIL import Image
import re
import streamlit as st
import os

class TesseractParser:
    def __init__(self):
        # Configurar ruta de Tesseract
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f" Tesseract encontrado en: {path}")
                break
        else:
            st.error(" Tesseract no encontrado. Instálalo desde: https://github.com/UB-Mannheim/tesseract/wiki")
    
    def parse_image(self, image_bytes):
        """Extrae texto de imagen usando Tesseract"""
        try:
            # Guardar temporalmente la imagen
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(image_bytes.getvalue())
                tmp_path = tmp.name
            
            # Abrir imagen y aplicar OCR
            image = Image.open(tmp_path)
            
            # Mejorar imagen para mejor OCR
            image = image.convert('L')  # Escala de grises
            image = image.point(lambda x: 0 if x < 128 else 255)  # Binarizar
            
            # Extraer texto con español
            text = pytesseract.image_to_string(image, lang='spa')
            
            # Limpiar archivo temporal
            os.unlink(tmp_path)
            
            return self._parse_text(text)
            
        except Exception as e:
            st.error(f"Error en OCR: {e}")
            return []
    
    def _parse_text(self, text):
        """Convierte texto a estructura de partidos"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Debug: mostrar líneas detectadas
        print(" Líneas detectadas:", lines)
        
        matches = []
        i = 0
        while i < len(lines):
            try:
                # Buscar patrón: [Equipo] [Odds] [Empate] [Odds] [Equipo] [Odds]
                if i + 5 < len(lines):
                    local = lines[i]
                    cuota_local = lines[i+1]
                    empate = lines[i+2]
                    cuota_empate = lines[i+3]
                    visitante = lines[i+4]
                    cuota_visitante = lines[i+5]
                    
                    # Verificar que tiene formato de partido
                    if (re.search(r'[+-]?\d+', cuota_local) and 
                        re.search(r'[+-]?\d+', cuota_visitante)):
                        
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
