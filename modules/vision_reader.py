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
    
    def is_odd(self, text: str) -> bool:
        """Detecta si un texto es una cuota"""
        cleaned = re.sub(r'\s+', '', text.strip())
        num_part = cleaned.replace('+', '').replace('-', '')
        try:
            val = float(num_part)
            # Cuotas americanas son >100, decimales entre 1 y 10
            return abs(val) >= 100 or (1 < val < 10)
        except:
            return False
    
    def is_team_name(self, text: str) -> bool:
        """Detecta si un texto es probable nombre de equipo"""
        if not text or len(text) < 3:
            return False
        
        # No debe ser un número
        if text.replace('.', '').replace('-', '').replace('+', '').isdigit():
            return False
        
        # No debe ser una fecha
        if re.match(r'\d{1,2}\s+[A-Za-z]{3}', text):
            return False
        
        # No debe ser una hora
        if re.match(r'\d{2}:\d{2}', text):
            return False
        
        # Palabras que no son equipos
        blacklist = ['empate', 'draw', 'vs', 'v', 'fc', 'cf', 'sc', 'ac', 'cd', 
                     'ud', 'sd', 'club', 'deportivo', 'real', 'united', 'city',
                     'athletic', 'sporting', 'racing', 'internacional']
        
        if text.lower() in blacklist:
            return False
        
        return True
    
    def clean_name(self, text: str) -> str:
        """Limpia el nombre del equipo"""
        # Quita códigos +XX al inicio
        text = re.sub(r'^\+\d+\s*', '', text)
        
        # Quita fechas al final (ej: "02 Mar 03:00")
        text = re.sub(r'\s*\d{1,2}\s+[A-Za-z]{3}\s*\d{2}:\d{2}$', '', text)
        
        # Quita códigos +XX en cualquier parte
        text = re.sub(r'\+\d+', '', text)
        
        # Quita caracteres especiales
        text = re.sub(r'[|•\-_=+*]', ' ', text)
        
        # Normaliza espacios
        text = ' '.join(text.split())
        
        return text.strip() if len(text) > 2 else ""
    
    def extract_words_with_coordinates(self, response):
        """Extrae palabras individuales con coordenadas"""
        word_list = []
        
        if not response.full_text_annotation or not response.full_text_annotation.pages:
            return word_list
        
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join(s.text for s in word.symbols).strip()
                        if not word_text:
                            continue
                        
                        # Calcular centro del bounding box
                        v = word.bounding_box.vertices
                        x = (v[0].x + v[2].x) / 2
                        y = (v[0].y + v[2].y) / 2
                        
                        word_list.append({
                            "text": word_text,
                            "x": x,
                            "y": y
                        })
        
        return word_list
    
    def parse_image(self, uploaded_file):
        """
        Procesa la imagen analizando palabra por palabra
        """
        if not self.client:
            return {
                'matches': [], 
                'raw_text': '', 
                'debug': [],
                'error': 'Cliente Google Vision no inicializado'
            }
        
        try:
            content = uploaded_file.getvalue()
            image = vision.Image(content=content)
            response = self.client.document_text_detection(image=image)
            
            # Guardar texto completo para debug
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # Extraer palabras con coordenadas
            word_list = self.extract_words_with_coordinates(response)
            
            if not word_list:
                return {
                    'matches': [], 
                    'raw_text': full_text, 
                    'debug': ['No se detectaron palabras en la imagen']
                }
            
            # Ordenar por Y (arriba a abajo)
            word_list.sort(key=lambda w: w["y"])
            
            matches = []
            debug_lines = []
            
            i = 0
            while i < len(word_list):
                current_word = word_list[i]["text"]
                
                # Buscar posible nombre de equipo
                if self.is_team_name(current_word):
                    home_raw = current_word
                    home = self.clean_name(home_raw)
                    
                    # Buscar 3 odds después
                    odds = []
                    j = i + 1
                    while j < len(word_list) and len(odds) < 3:
                        candidate = word_list[j]["text"]
                        if self.is_odd(candidate):
                            odds.append(candidate)
                        j += 1
                    
                    if len(odds) == 3:
                        # Buscar equipo visitante después de las odds
                        away = "Visitante no detectado"
                        k = j
                        while k < len(word_list):
                            candidate = word_list[k]["text"]
                            if self.is_team_name(candidate):
                                away = self.clean_name(candidate)
                                break
                            k += 1
                        
                        if home and away != "Visitante no detectado":
                            matches.append({
                                "home": home,
                                "away": away,
                                "odds": odds,
                                "home_odd": odds[0],
                                "draw_odd": odds[1],
                                "away_odd": odds[2],
                                "liga": "Detectada de imagen"
                            })
                            
                            debug_lines.append(f"✅ {home} vs {away} → {odds}")
                            
                            # Saltar al siguiente posible local
                            i = k + 1
                            continue
                
                i += 1
            
            # Si no se encontraron partidos con el método principal
            if not matches:
                debug_lines.append("❌ No se encontró patrón 'equipo + 3 odds + equipo'")
                debug_lines.append("🔍 Revisa que la imagen tenga formato claro")
            
            return {
                'matches': matches,
                'raw_text': full_text,
                'debug': debug_lines,
                'words_detected': len(word_list)
            }
            
        except Exception as e:
            st.error(f"Error en Google Vision: {e}")
            return {
                'matches': [], 
                'raw_text': '', 
                'debug': [f"Error: {str(e)}"],
                'error': str(e)
            }
