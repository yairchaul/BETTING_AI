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
    
    def parse_image(self, uploaded_file):
        """
        Procesa la imagen usando coordenadas para detectar partidos
        """
        if not self.client:
            return {'matches': [], 'raw_text': '', 'error': 'Cliente no inicializado'}
        
        try:
            content = uploaded_file.getvalue()
            image = vision.Image(content=content)
            response = client.document_text_detection(image=image)
            
            if not response.full_text_annotation:
                return {'matches': [], 'raw_text': ''}
            
            full_text = response.full_text_annotation.text
            
            # 1. Extraer palabras con sus coordenadas
            word_list = self._extract_words_with_coordinates(response)
            
            # 2. Agrupar por líneas (basado en coordenada Y)
            lines = self._group_by_lines(word_list)
            
            # 3. Detectar partidos en las líneas
            matches = self._detect_matches_from_lines(lines)
            
            return {
                'matches': matches,
                'raw_text': full_text,
                'debug': {
                    'words_detected': len(word_list),
                    'lines_detected': len(lines),
                    'matches_found': len(matches)
                }
            }
            
        except Exception as e:
            st.error(f"Error en Google Vision: {e}")
            return {'matches': [], 'raw_text': '', 'error': str(e)}
    
    def _extract_words_with_coordinates(self, response):
        """
        Extrae cada palabra con sus coordenadas (x, y) del centro
        """
        word_list = []
        
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    # Construir el texto completo del párrafo
                    paragraph_text = " ".join([
                        "".join([s.text for s in word.symbols]) 
                        for word in paragraph.words
                    ])
                    
                    # Calcular punto medio del bounding box
                    vertices = paragraph.bounding_box.vertices
                    avg_x = sum(v.x for v in vertices) / 4
                    avg_y = sum(v.y for v in vertices) / 4
                    
                    word_list.append({
                        "text": paragraph_text,
                        "x": avg_x,
                        "y": avg_y
                    })
        
        return word_list
    
    def _group_by_lines(self, word_list, tolerance=15):
        """
        Agrupa palabras por líneas basado en coordenada Y
        """
        if not word_list:
            return []
        
        # Ordenar por Y
        word_list.sort(key=lambda w: w["y"])
        
        lines = []
        current_line = [word_list[0]]
        
        for i in range(1, len(word_list)):
            if abs(word_list[i]["y"] - current_line[-1]["y"]) < tolerance:
                current_line.append(word_list[i])
            else:
                # Ordenar la línea actual por X (izquierda a derecha)
                current_line.sort(key=lambda w: w["x"])
                lines.append(current_line)
                current_line = [word_list[i]]
        
        # Agregar la última línea
        current_line.sort(key=lambda w: w["x"])
        lines.append(current_line)
        
        return lines
    
    def _detect_matches_from_lines(self, lines):
        """
        Detecta partidos en las líneas de texto
        """
        matches = []
        
        for line in lines:
            # Unir texto de la línea
            text_line = " ".join([w["text"] for w in line])
            
            # Buscar momios americanos (+/- seguido de 3-4 dígitos)
            odds = re.findall(r'[+-]\d{3,4}', text_line)
            
            if len(odds) >= 3:
                # Limpiar el texto
                clean_text = text_line
                
                # Quitar fechas (ej: "02 Mar 03:00")
                clean_text = re.sub(r'\d{1,2}\s+[A-Za-z]{3}\s+\d{2}:\d{2}', '', clean_text)
                
                # Quitar números sueltos (+43, etc)
                clean_text = re.sub(r'\+\s*\d+', '', clean_text)
                
                # Quitar las odds que ya extrajimos
                for odd in odds[:3]:
                    clean_text = clean_text.replace(odd, "")
                
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                # Intentar separar local y visitante
                # Método 1: Dividir por "vs" si existe
                if ' vs ' in clean_text.lower():
                    parts = re.split(r'\s+vs\s+', clean_text, flags=re.IGNORECASE)
                    if len(parts) == 2:
                        home = self._clean_team_name(parts[0])
                        away = self._clean_team_name(parts[1])
                        
                        if home and away:
                            matches.append({
                                "home": home,
                                "away": away,
                                "home_odd": odds[0],
                                "draw_odd": odds[1],
                                "away_odd": odds[2],
                                "liga": "Detectada de imagen",
                                "odds": odds[:3]
                            })
                            continue
                
                # Método 2: Dividir por espacios dobles
                parts = [p.strip() for p in clean_text.split("  ") if len(p.strip()) > 2]
                
                if len(parts) >= 2:
                    home = self._clean_team_name(parts[0])
                    away = self._clean_team_name(parts[-1])
                    
                    if home and away and home != away:
                        matches.append({
                            "home": home,
                            "away": away,
                            "home_odd": odds[0],
                            "draw_odd": odds[1],
                            "away_odd": odds[2],
                            "liga": "Detectada de imagen",
                            "odds": odds[:3]
                        })
        
        return matches
    
    def _clean_team_name(self, name):
        """
        Limpia el nombre del equipo
        """
        if not name:
            return ""
        
        # Eliminar números y caracteres especiales
        name = re.sub(r'[0-9+\-]', '', name)
        
        # Eliminar palabras comunes que no son parte del nombre
        common = ['FC', 'CF', 'SC', 'AC', 'CD', 'UD', 'SD', 'Club', 'Deportivo', 'Real']
        for word in common:
            name = name.replace(word, '')
        
        # Limpiar espacios
        name = ' '.join(name.split())
        
        return name.strip()
