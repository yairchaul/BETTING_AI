# modules/vision_reader.py
import re
import streamlit as st
from google.cloud import vision

class ImageParser:
    def __init__(self):
        """Inicializa el cliente de Google Vision"""
        try:
            self.client = vision.ImageAnnotatorClient.from_service_account_info(
                dict(st.secrets["google_credentials"])
            )
        except Exception as e:
            st.error(f"Error inicializando Google Vision: {e}")
            self.client = None

    def process_image(self, image_bytes):
        """Procesa la imagen y extrae pares de equipos"""
        if not self.client:
            return []
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                return []

            full_text = texts[0].description
            
            # Mostrar el texto raw para debug
            st.text("Texto raw detectado:")
            st.code(full_text)
            
            return self.parse_six_column_table(full_text)
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []

    def parse_six_column_table(self, text):
        """
        Interpreta una tabla de 6 columnas:
        Col1: Equipo Local
        Col2: Cuota Local
        Col3: Palabra "Empate"
        Col4: Cuota Empate
        Col5: Equipo Visitante
        Col6: Cuota Visitante
        """
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        matches = []
        
        # ============================================================================
        # PROCESAR LÍNEA POR LÍNEA BUSCANDO EL PATRÓN DE 6 ELEMENTOS
        # ============================================================================
        i = 0
        while i < len(lines):
            # Buscar una línea que contenga un equipo local (con letras)
            if i + 5 < len(lines):  # Necesitamos 6 elementos consecutivos
                
                # Verificar si tenemos el patrón completo
                posible_local = lines[i]
                posible_cuota_local = lines[i+1]
                posible_empate = lines[i+2]
                posible_cuota_empate = lines[i+3]
                posible_visitante = lines[i+4]
                posible_cuota_visitante = lines[i+5]
                
                # Validar el patrón
                if (self.is_team_name(posible_local) and
                    self.is_odds(posible_cuota_local) and
                    "Empate" in posible_empate and
                    self.is_odds(posible_cuota_empate) and
                    self.is_team_name(posible_visitante) and
                    self.is_odds(posible_cuota_visitante)):
                    
                    matches.append({
                        "home": self.clean_team_name(posible_local),
                        "away": self.clean_team_name(posible_visitante),
                        "all_odds": [
                            posible_cuota_local,
                            posible_cuota_empate,
                            posible_cuota_visitante
                        ]
                    })
                    
                    # Saltamos las 6 líneas procesadas
                    i += 6
                    continue
            
            i += 1
        
        # ============================================================================
        # SI NO ENCONTRÓ CON EL MÉTODO ANTERIOR, INTENTAR CON EXPRESIONES REGULARES
        # ============================================================================
        if not matches:
            # Buscar patrón en una sola línea
            for line in lines:
                # Patrón: Equipo, odds, "Empate", odds, Equipo, odds
                pattern = r'([A-Za-z\s]+)\s+([+-]\d{3,4})\s+Empate\s+([+-]\d{3,4})\s+([A-Za-z\s]+)\s+([+-]\d{3,4})'
                encontrado = re.search(pattern, line)
                
                if encontrado:
                    matches.append({
                        "home": encontrado.group(1).strip(),
                        "away": encontrado.group(4).strip(),
                        "all_odds": [
                            encontrado.group(2),
                            encontrado.group(3),
                            encontrado.group(5)
                        ]
                    })
        
        return matches

    def is_team_name(self, text):
        """Determina si un texto es probable nombre de equipo"""
        if not text or len(text) < 2:
            return False
        
        # No debe ser una odds
        if re.match(r'^[+-]\d{3,4}$', text):
            return False
        
        # No debe ser "Empate"
        if "Empate" in text:
            return False
        
        # Debe contener letras
        if not re.search(r'[A-Za-z]', text):
            return False
        
        return True

    def is_odds(self, text):
        """Determina si un texto es una odds"""
        return bool(re.match(r'^[+-]\d{3,4}$', text))

    def clean_team_name(self, name):
        """Limpia el nombre del equipo"""
        # Eliminar números y caracteres especiales
        name = re.sub(r'[0-9+\-]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name


# Función de respaldo para entrada manual
def procesar_texto_manual(texto):
    """Procesa texto ingresado manualmente"""
    lineas = texto.split('\n')
    partidos = []
    for linea in lineas:
        if ' vs ' in linea.lower():
            teams = re.split(r' vs ', linea, flags=re.IGNORECASE)
            if len(teams) == 2:
                partidos.append({
                    "home": teams[0].strip(), 
                    "away": teams[1].strip(),
                    "all_odds": ['N/A', 'N/A', 'N/A']
                })
    return partidos
