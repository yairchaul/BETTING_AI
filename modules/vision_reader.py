# modules/vision_reader.py
"""
Parser de imágenes mejorado para Caliente.mx
Detecta nombres completos de equipos de Liga MX y Liga de Expansión
"""
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
        
        # Diccionario de nombres completos de equipos
        self.team_names = {
            # Liga MX
            'puebla': 'Puebla',
            'tigres': 'Tigres UANL',
            'tigres uanl': 'Tigres UANL',
            'monterrey': 'Monterrey',
            'rayados': 'Monterrey',
            'queretaro': 'Querétaro FC',
            'querétaro': 'Querétaro FC',
            'atlas': 'Atlas',
            'tijuana': 'Club Tijuana',
            'xolos': 'Club Tijuana',
            'america': 'Club América',
            'club américa': 'Club América',
            'chivas': 'Guadalajara',
            'guadalajara': 'Guadalajara',
            'cruz azul': 'Cruz Azul',
            'pumas': 'Pumas UNAM',
            'unam': 'Pumas UNAM',
            'santos': 'Santos Laguna',
            'santos laguna': 'Santos Laguna',
            'leon': 'Club León',
            'león': 'Club León',
            'pachuca': 'Pachuca',
            'necaxa': 'Necaxa',
            'toluca': 'Toluca',
            'mazatlan': 'Mazatlán FC',
            'mazatlán': 'Mazatlán FC',
            'san luis': 'Atlético San Luis',
            'atletico san luis': 'Atlético San Luis',
            'juarez': 'FC Juárez',
            'juárez': 'FC Juárez',
            'fc juárez': 'FC Juárez',
            
            # Liga de Expansión MX
            'tapatio': 'CD Tapatío',
            'tapatío': 'CD Tapatío',
            'cd tapatio': 'CD Tapatío',
            'venados': 'Venados FC',
            'venados fc': 'Venados FC',
            'atlante': 'Atlante',
            'irapuato': 'Irapuato FC',
            'irapuato fc': 'Irapuato FC',
            'club atletico la paz': 'Club Atlético La Paz',
            'atletico la paz': 'Club Atlético La Paz',
            'jaiba': 'Jaiba Brava',
            'jaiba brava': 'Jaiba Brava',
            'tepatitlan': 'CD Tepatitlán de Morelos',
            'tepatitlán': 'CD Tepatitlán de Morelos',
            'cd tepatitlan': 'CD Tepatitlán de Morelos',
            'correcaminos': 'Correcaminos UAT',
            'morelia': 'Atlético Morelia',
            'oaxaca': 'Alebrijes de Oaxaca',
            'dorados': 'Dorados de Sinaloa',
            'mineros': 'Mineros de Zacatecas',
            'zacatecas': 'Mineros de Zacatecas',
            'fc': 'FC',  # Placeholder
        }

    def normalize_name(self, name):
        """Normaliza un nombre para búsqueda"""
        if not name:
            return ""
        name = name.lower().strip()
        name = re.sub(r'[^\w\s]', '', name)  # Eliminar puntuación
        return name

    def get_full_team_name(self, partial_name):
        """Obtiene el nombre completo del equipo"""
        if not partial_name:
            return partial_name
        
        normalized = self.normalize_name(partial_name)
        
        # Búsqueda directa
        if normalized in self.team_names:
            return self.team_names[normalized]
        
        # Búsqueda por coincidencia parcial
        for key, full_name in self.team_names.items():
            if key in normalized or normalized in key:
                return full_name
        
        # Si no se encuentra, devolver el original pero capitalizado
        return partial_name.title()

    def process_image(self, image_bytes):
        """Procesa la imagen y extrae palabras con coordenadas"""
        if not self.client:
            return []
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            
            if not response.text_annotations:
                return []
            
            words_with_coords = []
            for annotation in response.text_annotations[1:]:
                vertices = annotation.bounding_poly.vertices
                if vertices:
                    x = sum(v.x for v in vertices) / 4
                    y = sum(v.y for v in vertices) / 4
                    
                    words_with_coords.append({
                        'text': annotation.description,
                        'x': x,
                        'y': y
                    })
            
            return self._group_by_visual_structure(words_with_coords)
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []
    
    def _group_by_visual_structure(self, words):
        """Agrupa palabras por proximidad visual y detecta partidos"""
        if not words:
            return []
        
        # Ordenar por posición Y (de arriba a abajo)
        words.sort(key=lambda w: w['y'])
        
        # Agrupar en líneas (misma Y aproximada)
        lines = []
        current_line = [words[0]]
        y_threshold = 15  # Píxeles de tolerancia
        
        for word in words[1:]:
            if abs(word['y'] - current_line[-1]['y']) < y_threshold:
                current_line.append(word)
            else:
                # Ordenar la línea por X (izquierda a derecha)
                current_line.sort(key=lambda w: w['x'])
                lines.append(current_line)
                current_line = [word]
        
        if current_line:
            current_line.sort(key=lambda w: w['x'])
            lines.append(current_line)
        
        # Convertir líneas a texto
        text_lines = [' '.join([w['text'] for w in line]) for line in lines]
        
        # Detectar partidos en formato de 6 elementos
        matches = self._parse_matches(text_lines)
        
        return matches
    
    def _parse_matches(self, text_lines):
        """Parsea las líneas de texto para encontrar partidos"""
        matches = []
        i = 0
        
        while i < len(text_lines):
            line = text_lines[i]
            
            # Buscar patrón: Equipo + Odds + "Empate" + Odds + Equipo + Odds
            parts = line.split()
            
            # Si la línea tiene al menos 6 elementos
            if len(parts) >= 6:
                # Intentar identificar odds (números con + o -)
                odds_positions = []
                for j, part in enumerate(parts):
                    if re.match(r'[+-]\d+', part):
                        odds_positions.append(j)
                
                # Si encontramos al menos 3 odds
                if len(odds_positions) >= 3:
                    # La primera odds es la del local
                    local_odds_idx = odds_positions[0]
                    # La segunda odds es la del empate
                    draw_odds_idx = odds_positions[1]
                    # La tercera odds es la del visitante
                    away_odds_idx = odds_positions[2]
                    
                    # El equipo local es todo antes de la primera odds
                    local = ' '.join(parts[:local_odds_idx]).strip()
                    # El equipo visitante es todo entre la segunda y tercera odds
                    away = ' '.join(parts[draw_odds_idx+1:away_odds_idx]).strip() if draw_odds_idx+1 < away_odds_idx else ''
                    
                    # Si no encontramos visitante, puede estar en la siguiente línea
                    if not away and i+1 < len(text_lines):
                        away = text_lines[i+1].strip()
                        i += 1  # Saltar la siguiente línea
                    
                    # Obtener nombres completos
                    full_local = self.get_full_team_name(local)
                    full_away = self.get_full_team_name(away)
                    
                    matches.append({
                        'home': full_local,
                        'away': full_away,
                        'all_odds': [
                            parts[local_odds_idx],
                            parts[draw_odds_idx],
                            parts[away_odds_idx]
                        ]
                    })
                    i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return matches