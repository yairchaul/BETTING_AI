import os
import pytesseract
from PIL import Image
import streamlit as st
import urllib.request
import re

class TesseractParser:
    def __init__(self):
        # Configurar ruta de Tesseract
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            st.success(" Tesseract encontrado")
        else:
            st.error(f" Tesseract no encontrado en {tesseract_path}")
            return
        
        # Configurar TESSDATA_PREFIX
        tessdata_path = r'C:\Program Files\Tesseract-OCR\tessdata'
        if os.path.exists(tessdata_path):
            os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR'
            st.success(" TESSDATA_PREFIX configurado")
        else:
            st.error(f" Carpeta tessdata no encontrada en {tessdata_path}")
            return
        
        # Verificar idioma español
        self._ensure_spanish()
    
    def _ensure_spanish(self):
        """Asegura que el idioma español esté disponible"""
        tessdata_path = r'C:\Program Files\Tesseract-OCR\tessdata'
        spanish_path = os.path.join(tessdata_path, 'spa.traineddata')
        
        if not os.path.exists(spanish_path):
            st.warning(" Idioma español no encontrado. Instalando...")
            self._install_spanish()
        else:
            st.success(" Idioma español encontrado")
    
    def _install_spanish(self):
        """Instala el idioma español automáticamente"""
        tessdata_path = r'C:\Program Files\Tesseract-OCR\tessdata'
        spa_url = 'https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata'
        spa_file = os.path.join(tessdata_path, 'spa.traineddata')
        
        try:
            urllib.request.urlretrieve(spa_url, spa_file)
            st.success(" Idioma español instalado correctamente")
        except Exception as e:
            st.error(f" Error instalando español: {e}")
            st.info("Usando inglés como alternativa")
    
    def parse_image(self, image_bytes):
        """Extrae texto de imagen usando Tesseract"""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(image_bytes.getvalue())
                tmp_path = tmp.name
            
            # Procesar imagen para mejor OCR
            image = Image.open(tmp_path)
            image = image.convert('L')  # Escala de grises
            image = image.point(lambda x: 0 if x < 128 else 255)  # Binarizar
            
            # Intentar con español, fallback a inglés
            try:
                text = pytesseract.image_to_string(image, lang='spa')
            except:
                text = pytesseract.image_to_string(image, lang='eng')
                st.info("Usando OCR en inglés (español no disponible)")
            
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
        if 'debug_mode' in st.session_state and st.session_state.debug_mode:
            st.write(" Líneas detectadas:", lines)
        
        matches = []
        i = 0
        while i < len(lines):
            try:
                # Buscar patrón de 6 líneas por partido
                if i + 5 < len(lines):
                    local = lines[i]
                    cuota_local = lines[i+1]
                    empate = lines[i+2]
                    cuota_empate = lines[i+3]
                    visitante = lines[i+4]
                    cuota_visitante = lines[i+5]
                    
                    # Verificar que tiene formato de partido (números con + o -)
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
            except Exception as e:
                if 'debug_mode' in st.session_state and st.session_state.debug_mode:
                    st.write(f"Error en línea {i}: {e}")
                i += 1
        
        return matches
