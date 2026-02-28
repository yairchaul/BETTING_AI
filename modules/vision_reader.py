import re
import streamlit as st
import pandas as pd
from google.cloud import vision

def clean_ocr_noise(text):
    """Limpia fechas, horas y basura visual (+43)"""
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d+', '', text)
    return text.strip()

def read_ticket_image(uploaded_file):
    """
    Función principal llamada por main.py.
    """
    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        content = uploaded_file.getvalue()
        image = vision.Image(content=content)
        
        # document_text_detection es ideal para capturas de pantalla con tablas
        response = client.document_text_detection(image=image)
        matches = []

        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    # Agrupar texto por párrafos para no perder el contexto horizontal
                    paragraphs = []
                    for para in block.paragraphs:
                        p_text = " ".join(["".join([s.text for s in w.symbols]) for w in para.words])
                        paragraphs.append(p_text)
                    
                    full_block_text = "\n".join(paragraphs)
                    
                    # Buscamos los 3 momios (+123, -450, etc)
                    odds = re.findall(r'[+-]\d{3,4}', full_block_text)
                    
                    if len(odds) >= 3:
                        clean_text = clean_ocr_noise(full_block_text)
                        for o in odds:
                            clean_text = clean_text.replace(o, "")
                        
                        lines = [l.strip() for l in clean_text.split('\n') if len(l.strip()) > 2]
                        
                        if len(lines) >= 2:
                            # Retornamos la estructura que el main.py y cerebro.py esperan
                            matches.append({
                                "home": lines[0],
                                "away": lines[1],
                                "all_odds": odds[:3], # Fallback para cerebro
                                "odds": odds[:3],     # Formato estándar
                                "context": f"{lines[0]} vs {lines[1]}"
                            })
        return matches
    except Exception as e:
        st.error(f"Error en vision_reader: {e}")
        return []
