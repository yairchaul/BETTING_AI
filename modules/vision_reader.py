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
        """Procesa la imagen y extrae palabras con coordenadas"""
        if not self.client:
            return []
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            
            if not response.text_annotations:
                return []
            
            # Extraer cada palabra con sus coordenadas
            words_with_coords = []
            for annotation in response.text_annotations[1:]:  # Saltar el primer elemento (todo el texto)
                vertices = annotation.bounding_poly.vertices
                if vertices:
                    # Calcular centro del bounding box
                    x = sum(v.x for v in vertices) / 4
                    y = sum(v.y for v in vertices) / 4
                    
                    # Calcular altura aproximada (para detectar tamaños de letra)
                    height = abs(vertices[0].y - vertices[2].y) if vertices else 0
                    
                    words_with_coords.append({
                        'text': annotation.description,
                        'x': x,
                        'y': y,
                        'height': height,
                        'confidence': annotation.confidence if hasattr(annotation, 'confidence') else 1.0
                    })
            
            return self._group_by_visual_structure(words_with_coords)
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []
    
    def _group_by_visual_structure(self, words):
        """
        Agrupa palabras por proximidad visual (misma línea, mismo bloque)
        """
        # Ordenar por coordenada Y (de arriba a abajo)
        words.sort(key=lambda w: w['y'])
        
        # Agrupar en líneas (tolerancia de 15 píxeles en Y)
        lines = []
        current_line = [words[0]]
        
        for word in words[1:]:
            if abs(word['y'] - current_line[-1]['y']) < 15:
                current_line.append(word)
            else:
                # Ordenar línea por X (izquierda a derecha)
                current_line.sort(key=lambda w: w['x'])
                lines.append(current_line)
                current_line = [word]
        lines.append(current_line)
        
        # Ahora detectar bloques basados en espaciado vertical
        blocks = []
        current_block = [lines[0]]
        
        for i in range(1, len(lines)):
            prev_line = lines[i-1]
            curr_line = lines[i]
            
            # Calcular espacio vertical entre líneas
            prev_y = sum(w['y'] for w in prev_line) / len(prev_line)
            curr_y = sum(w['y'] for w in curr_line) / len(curr_line)
            gap = curr_y - prev_y
            
            # Si el gap es grande (> 30 píxeles), es un nuevo bloque
            if gap > 30:
                blocks.append(current_block)
                current_block = [curr_line]
            else:
                current_block.append(curr_line)
        blocks.append(current_block)
        
        # Procesar cada bloque para extraer partidos
        return self._extract_matches_from_blocks(blocks)
    
    def _extract_matches_from_blocks(self, blocks):
        """
        Extrae partidos de cada bloque visual
        """
        matches = []
        
        for block in blocks:
            # Un bloque debe tener al menos 6 líneas para ser un partido
            if len(block) < 6:
                continue
            
            # Extraer texto de cada línea
            block_texts = [' '.join([w['text'] for w in line]) for line in block]
            
            # Detectar patrón: línea1 (metadata), línea2 (local), línea3 (visitante), línea4 (fecha), luego cuotas
            if len(block_texts) >= 5:
                # Posible metadata (número con signo)
                metadata = block_texts[0] if re.match(r'^[+-]\d+$', block_texts[0]) else ''
                
                # Equipo local y visitante
                home = block_texts[1] if len(block_texts) > 1 else ''
                away = block_texts[2] if len(block_texts) > 2 else ''
                fecha = block_texts[3] if len(block_texts) > 3 else ''
                
                # Extraer cuotas de las líneas restantes
                odds = []
                for i in range(4, min(7, len(block_texts))):
                    # Buscar números con signo en la línea
                    found_odds = re.findall(r'[+-]\d+', block_texts[i])
                    if found_odds:
                        odds.extend(found_odds)
                
                if home and away and len(odds) >= 2:
                    # Completar si faltan odds
                    while len(odds) < 3:
                        odds.append('N/A')
                    
                    matches.append({
                        'home': home,
                        'away': away,
                        'all_odds': odds[:3],
                        'metadata': metadata,
                        'fecha': fecha
                    })
        
        return matches