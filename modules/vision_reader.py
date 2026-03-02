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
            response = self.client.text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                return []

            # El primer elemento (index 0) es TODO el texto detectado
            full_text = texts[0].description
            return self.smart_parse(full_text)
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []

    def smart_parse(self, text):
        """Lógica para extraer equipos ignorando ruido de cuotas y fechas"""
        lines = text.split('\n')
        matches = []
        
        # 1. Limpiamos líneas que son solo números o fechas
        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Ignorar si es solo una cuota (ej: +120, -110, 2.50)
            if re.match(r'^[+-]?\d+[.,]?\d*$', line):
                continue
            # Ignorar si es solo una hora o fecha corta (ej: 12:00, 02 Mar)
            if re.match(r'^\d{2}:\d{2}$', line):
                continue
            if re.match(r'^\d{1,2}\s+[A-Za-z]{3}', line):
                continue
            # Ignorar palabras de control
            if line.lower() in ['empate', 'draw', 'vs', 'v', 'cerrar', 'apuesta', 'mis']:
                continue
            
            # Limpiar caracteres especiales
            line = re.sub(r'[|•\-_=+*]', ' ', line)
            line = re.sub(r'\s+', ' ', line).strip()
            
            if len(line) > 2:
                clean_lines.append(line)

        # 2. Extraer odds (para usarlas después)
        all_odds = re.findall(r'[+-]\d{3,4}', text)
        
        # 3. Agrupar por pares (Local vs Visitante)
        i = 0
        odds_index = 0
        while i < len(clean_lines) - 1 and odds_index + 2 < len(all_odds):
            local = clean_lines[i]
            visitante = clean_lines[i + 1]
            
            # Limpiar nombres
            local = self.fix_common_names(local)
            visitante = self.fix_common_names(visitante)
            
            # Verificar que sean nombres válidos
            if self.is_valid_team_pair(local, visitante):
                matches.append({
                    "home": local,
                    "away": visitante,
                    "all_odds": all_odds[odds_index:odds_index + 3]
                })
                odds_index += 3
                i += 2
            else:
                i += 1
        
        # Si no encuentra con el método anterior, intentar buscar "vs"
        if not matches:
            for line in clean_lines:
                if ' vs ' in line.lower():
                    parts = re.split(r'\s+vs\s+', line, flags=re.IGNORECASE)
                    if len(parts) == 2:
                        matches.append({
                            "home": self.fix_common_names(parts[0].strip()),
                            "away": self.fix_common_names(parts[1].strip()),
                            "all_odds": ['N/A', 'N/A', 'N/A']
                        })
        
        return matches

    def is_valid_team_pair(self, t1, t2):
        """Valida que no estemos emparejando un equipo con un nombre de liga o botón"""
        bad_words = ['liga', 'champions', 'premier', 'apuesta', 'vivo', 'finalizado', 
                     'score', 'points', 'calendar', 'schedule', 'filter']
        combined = (t1 + ' ' + t2).lower()
        return not any(word in combined for word in bad_words) and len(t1) > 2 and len(t2) > 2

    def fix_common_names(self, name):
        """Corrige nombres que el OCR a veces corta o confunde"""
        name = name.replace('|', '').strip()
        # Mapeo de nombres cortos a largos
        corrections = {
            "PSG": "Paris Saint Germain",
            "M'gladbach": "Borussia Monchengladbach",
            "U. Berlin": "Union Berlin",
            "Le Havre AC": "Le Havre",
            "Real": "Real Madrid",  # Solo como ejemplo, esto debería ser más específico
            "Barca": "Barcelona",
            "Atleti": "Atletico Madrid"
        }
        return corrections.get(name, name)

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
