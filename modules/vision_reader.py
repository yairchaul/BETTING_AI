import re
import streamlit as st
from google.cloud import vision

def clean_ocr_noise(text):
    """Elimina fechas (28 Feb), horas (03:00) y mercados (+43)"""
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{2}:\d{2}', '', text)
    text = re.sub(r'\+\s*\d+', '', text)
    return text.strip()

def read_ticket_image(uploaded_file):
    """
    Función principal llamada por main.py.
    Retorna una lista de diccionarios con la estructura que tu cerebro.py espera.
    """
    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        content = uploaded_file.getvalue()
        image = vision.Image(content=content)
        
        # document_text_detection es el motor más potente para capturas de pantalla
        response = client.document_text_detection(image=image)
        matches = []

        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    # Extraemos el texto del bloque completo para no separar equipos de momios
                    block_text = ""
                    for para in block.paragraphs:
                        para_text = " ".join(["".join([s.text for s in w.symbols]) for w in para.words])
                        block_text += para_text + "\n"
                    
                    # Buscamos los 3 momios americanos (+123, -450, etc)
                    odds = re.findall(r'[+-]\d{3,4}', block_text)
                    
                    if len(odds) >= 3:
                        # Limpiamos el texto para aislar solo los nombres de los equipos
                        clean_text = clean_ocr_noise(block_text)
                        for o in odds:
                            clean_text = clean_text.replace(o, "")
                        
                        # Dividimos el texto limpio en líneas
                        lines = [l.strip() for l in clean_text.split('\n') if len(l.strip()) > 2]
                        
                        if len(lines) >= 2:
                            # Estructura que consume tu main.py
                            matches.append({
                                "home": lines[0],
                                "away": lines[1],
                                "odds": odds[:3], # Usado por el cerebro optimizado
                                "all_odds": odds[:3], # Fallback para tu cerebro actual
                                "context": f"{lines[0]} vs {lines[1]}"
                            })
        
        return matches

    except Exception as e:
        st.error(f"Error en vision_reader: {e}")
        return []
