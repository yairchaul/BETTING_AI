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
        """Procesa la imagen y extrae pares de equipos usando coordenadas"""
        if not self.client:
            return []
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            
            raw_elements = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        # Unimos palabras del párrafo para nombres compuestos (ej: "Real Madrid")
                        text = " ".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                        v = paragraph.bounding_box.vertices
                        y_center = sum([p.y for p in v]) / 4
                        x_center = sum([p.x for p in v]) / 4
                        raw_elements.append({"text": text, "y": y_center, "x": x_center})

            if not raw_elements:
                return []

            # 1. Ordenar verticalmente (Y)
            raw_elements.sort(key=lambda x: x['y'])

            # 2. Agrupar en filas (Umbral de 25px para evitar mezclar partidos)
            rows = []
            current_row = [raw_elements[0]]
            for i in range(1, len(raw_elements)):
                if abs(raw_elements[i]['y'] - current_row[-1]['y']) < 25:
                    current_row.append(raw_elements[i])
                else:
                    rows.append(current_row)
                    current_row = [raw_elements[i]]
            rows.append(current_row)

            matches = []
            blacklist = ["empate", "vix", "en vivo", "apostar", "ver", "liga mx", "hoy", "mañana"]

            for row in rows:
                # Ordenar cada fila de izquierda a derecha (X)
                row.sort(key=lambda x: x['x'])
                
                # Filtrar nombres de equipos y capturar cuotas
                clean_names = []
                odds_in_row = []
                
                for item in row:
                    txt = item['text'].strip()
                    # Si es una cuota (formato +120 o -150)
                    if re.match(r'^[+-]\d{3,4}$', txt):
                        odds_in_row.append(txt)
                    # Si es un nombre válido (sin números, no blacklist, largo > 2)
                    elif not any(char.isdigit() for char in txt) and txt.lower() not in blacklist and len(txt) > 2:
                        clean_names.append(txt)

                # REGLA: Necesitamos al menos 2 nombres (Local y Visitante)
                if len(clean_names) >= 2:
                    # El primero a la izquierda es Home, el último a la derecha es Away
                    home = clean_names[0]
                    away = clean_names[-1]
                    
                    if home.lower() != away.lower():
                        # Si no detectó 3 cuotas exactas, rellenamos con N/A
                        final_odds = odds_in_row if len(odds_in_row) == 3 else ['N/A', 'N/A', 'N/A']
                        
                        matches.append({
                            "home": home,
                            "away": away,
                            "all_odds": final_odds
                        })
            
            return matches
            
        except Exception as e:
            st.error(f"Error crítico en Vision Reader: {e}")
            return []

def procesar_texto_manual(texto):
    """Procesa texto ingresado manualmente (Formato: Equipo A vs Equipo B)"""
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
