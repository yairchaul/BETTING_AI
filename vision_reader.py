import streamlit as st
import re

try:
    from google.cloud import vision
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ModuleNotFoundError:
    GOOGLE_VISION_AVAILABLE = False
    vision = None
    service_account = None

class ImageParser:
    def __init__(self):
        self.client = None
        if GOOGLE_VISION_AVAILABLE and "gcp_service_account" in st.secrets:
            try:
                creds = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"]
                )
                self.client = vision.ImageAnnotatorClient(credentials=creds)
            except:
                self.client = None
    
    def process_image(self, image_bytes):
        """Procesa la imagen y devuelve líneas agrupadas por altura (Y)"""
        if not self.client:
            return self._get_test_data()
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            
            if response.error.message or not response.text_annotations:
                return []
            
            words = []
            for ann in response.text_annotations[1:]:
                if ann.bounding_poly.vertices:
                    v = ann.bounding_poly.vertices
                    x = sum(p.x for p in v) / 4
                    y = sum(p.y for p in v) / 4
                    words.append({"text": ann.description, "x": x, "y": y})
            
            return self._get_clean_lines(words)
        except Exception as e:
            st.error(f"Error: {e}")
            return []
    
    def _get_clean_lines(self, words):
        """Agrupa palabras por altura (Y) para formar líneas"""
        if not words:
            return []
        words.sort(key=lambda w: w["y"])
        lines = []
        current = [words[0]]
        for w in words[1:]:
            if abs(w["y"] - current[-1]["y"]) < 15:
                current.append(w)
            else:
                current.sort(key=lambda x: x["x"])
                lines.append([w["text"] for w in current])
                current = [w]
        if current:
            current.sort(key=lambda x: x["x"])
            lines.append([w["text"] for w in current])
        return lines
    
    def _get_test_data(self):
        """Datos de prueba cuando no hay Google Vision"""
        return [
            ["Galatasaray", "+350", "Empate", "+295", "Liverpool", "-139"],
            ["Barcelona", "+210", "Empate", "+240", "Real", "Madrid", "+130"],
            ["Piera", "Rodriguez", "-154", "Sam", "Hughes", "+120"]
        ]
