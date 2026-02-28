import re
import streamlit as st
from google.cloud import vision

def clean_ocr_noise(text):
    """Elimina fechas, horas y basura visual como '+ 43'"""
    # Elimina patrones como '28 Feb 03:00' o '+ 43'
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d+', '', text)
    return text.strip()

def read_ticket_image(uploaded_file):
    """
    Función principal llamada por main.py.
    Extrae partidos y momios de la imagen.
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
                    # Unir texto del bloque para mantener contexto de fila
                    block_text = ""
                    for para in block.paragraphs:
                        para_text = " ".join(["".join([s.text for s in w.symbols]) for w in para.words])
                        block_text += para_text + "\n"
                    
                    # Detectar exactamente 3 momios (ej: -175, +320, +340)
                    odds = re.findall(r'[+-]\d{3,4}', block_text)
                    
                    if len(odds) >= 3:
                        clean_text = clean_ocr_noise(block_text)
                        for o in odds:
                            clean_text = clean_text.replace(o, "")
                        
                        lines = [l.strip() for l in clean_text.split('\n') if len(l.strip()) > 2]
                        
                        if len(lines) >= 2:
                            # Estructura que main.py espera
                            matches.append({
                                "home": lines[0],    # Ej: Logan Lightning
                                "away": lines[1],    # Ej: North Star
                                "odds": odds[:3],    # Los 3 momios detectados
                                "context": f"{lines[0]} vs {lines[1]}"
                            })
        return matches
    except Exception as e:
        st.error(f"Error en vision_reader: {e}")
        return []
