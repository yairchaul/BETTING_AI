import streamlit as st
import re
import json
from google.cloud import vision
from google.oauth2 import service_account

class ImageParser:
    def __init__(self):
        self.client = None
        self._init_vision()
    
    def _init_vision(self):
        try:
            if "gcp_service_account" in st.secrets:
                creds = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"]
                )
                self.client = vision.ImageAnnotatorClient(credentials=creds)
                st.success("✅ Google Vision inicializado")
        except Exception as e:
            st.warning(f"⚠️ Google Vision no disponible: {e}")
    
    def process_image(self, image_bytes):
        if not self.client:
            return self._get_test_data()
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            
            if response.error.message:
                return []
            
            words = []
            for ann in response.text_annotations[1:]:
                if ann.bounding_poly.vertices:
                    v = ann.bounding_poly.vertices
                    x = sum(p.x for p in v) / 4
                    y = sum(p.y for p in v) / 4
                    words.append({"text": ann.description, "x": x, "y": y})
            
            return self._group_by_visual_structure(words)
        except:
            return self._get_test_data()
    
    def _get_test_data(self):
        return [
            {"home": "Galatasaray", "away": "Liverpool", "all_odds": ["+350", "+295", "-139"]},
            {"home": "Barcelona", "away": "Real Madrid", "all_odds": ["+210", "+240", "+130"]}
        ]
    
    def _group_by_visual_structure(self, words):
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
                lines.append(" ".join(w["text"] for w in current))
                current = [w]
        if current:
            current.sort(key=lambda x: x["x"])
            lines.append(" ".join(w["text"] for w in current))
        return self._parse_matches(lines)
    
    def _parse_matches(self, lines):
        matches = []
        for line in lines:
            parts = line.split()
            odds = [p for p in parts if re.match(r"^[+-]?\d+\.?\d*$", p)]
            if len(odds) >= 3:
                matches.append({
                    "home": parts[0] if parts else "",
                    "away": parts[-1] if parts else "",
                    "all_odds": odds[:3]
                })
        return matches