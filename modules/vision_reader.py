# modules/ocr_reader.py
import re
import streamlit as st
from google.cloud import vision

class ImageParser:
    def __init__(self):
        """Inicializa el cliente de Google Vision usando secrets"""
        try:
            self.client = vision.ImageAnnotatorClient.from_service_account_info(
                dict(st.secrets["google_credentials"])
            )
        except Exception as e:
            st.error(f"Error inicializando Google Vision: {e}")
            self.client = None
    
    def clean_ocr_noise(self, text):
        """Elimina ruidos de la interfaz y nombres de ligas."""
        # Eliminar fechas, horas y marcadores
        text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d{2}:\d{2}', '', text)
        text = re.sub(r'\+\s*\d+', '', text)
        
        # Lista negra de palabras que NO son equipos
        blacklist = [
            "Europa", "Rumania", "Turquía", "Italia", "Liga 2", "Liga 3", 
            "TFF League", "Primavera", "Championship", "Resultado", "Final", 
            "1", "X", "2", "Directo", "Hoy", "Mañana", "Puntos", "Score",
            "Points", "Asia", "Australia", "Europa", "Fútbol", "Mujeres",
            "Women", "International", "Euro", "Championship", "Qualifiers",
            "Sub-19", "U19", "State League", "Premier League", "National League"
        ]
        for word in blacklist:
            text = text.replace(word, "")
        
        return text.strip()
    
    def normalize_team_name(self, name):
        """Normaliza nombres de equipos para mejor matching"""
        # Eliminar números y caracteres especiales
        name = re.sub(r'[0-9+\-]', '', name)
        # Eliminar palabras comunes
        common = ['FC', 'CF', 'SC', 'AC', 'CD', 'UD', 'SD', 'Club', 'Deportivo']
        for word in common:
            name = name.replace(word, '')
        # Limpiar espacios
        name = ' '.join(name.split())
        return name.strip()
    
    def parse_image(self, uploaded_file):
        """Procesa la imagen con Google Vision y extrae los partidos"""
        
        if not self.client:
            st.error("Google Vision no inicializado")
            return {'matches': [], 'raw_text': ''}
        
        try:
            content = uploaded_file.getvalue()
            image = vision.Image(content=content)
            response = self.client.text_detection(image=image)
            
            if not response.text_annotations:
                return {'matches': [], 'raw_text': ''}
            
            full_text = response.text_annotations[0].description
            
            # Extraer momios americanos (+/- 3 o 4 dígitos)
            all_odds = re.findall(r'[+-]\d{3,4}', full_text)
            
            # Limpiar texto
            clean_text = self.clean_ocr_noise(full_text)
            for odd in all_odds:
                clean_text = clean_text.replace(odd, "")
            
            # Filtrar líneas que realmente parezcan equipos
            lines = [l.strip() for l in clean_text.split('\n') if len(l.strip()) > 3]
            
            matches = []
            used_indices = set()
            
            # Buscar patrones de partidos (dos equipos consecutivos con odds)
            for i in range(len(lines) - 1):
                if i in used_indices:
                    continue
                    
                line1 = lines[i]
                line2 = lines[i + 1] if i + 1 < len(lines) else ""
                
                # Verificar si hay odds disponibles
                odd_idx = len(matches) * 3
                if odd_idx + 2 < len(all_odds):
                    # Normalizar nombres
                    home = self.normalize_team_name(line1)
                    away = self.normalize_team_name(line2)
                    
                    # Validar que ambos nombres tengan sentido (no sean números o palabras vacías)
                    if (len(home) > 2 and len(away) > 2 and 
                        not home.isdigit() and not away.isdigit()):
                        
                        matches.append({
                            "home": home,
                            "away": away,
                            "odds": all_odds[odd_idx:odd_idx + 3],
                            "liga": "Detectada de imagen"
                        })
                        used_indices.add(i)
                        used_indices.add(i + 1)
            
            # SI NO HAY MATCHES, DEVOLVER LISTA VACÍA (NO FALLBACK)
            return {
                'matches': matches,
                'raw_text': full_text,
                'odds_detected': all_odds
            }
            
        except Exception as e:
            st.error(f"Error en OCR: {e}")
            return {'matches': [], 'raw_text': '', 'odds_detected': []}
