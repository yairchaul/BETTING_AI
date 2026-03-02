# modules/vision_reader.py (versión mejorada)
import re
import streamlit as st
from google.cloud import vision
import numpy as np
from PIL import Image
import io

def detect_device_type(image_bytes):
    """Detecta si la imagen es de PC o celular por dimensiones"""
    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size
    aspect_ratio = width / height
    return "PC" if aspect_ratio > 1.2 else "CELULAR"

def extract_structured_data(text_annotations):
    """
    Convierte las anotaciones de Google Vision en datos estructurados
    con coordenadas para entender la disposición de la imagen
    """
    if not text_annotations:
        return []
    
    full_text = text_annotations[0].description
    all_blocks = []
    
    # Extraer cada palabra con su bounding box
    for annotation in text_annotations[1:]:  # Saltamos el primero que es todo el texto
        vertices = annotation.bounding_poly.vertices
        if vertices:
            # Calcular centro del bounding box
            x = (vertices[0].x + vertices[2].x) / 2
            y = (vertices[0].y + vertices[2].y) / 2
            all_blocks.append({
                'text': annotation.description,
                'x': x,
                'y': y,
                'confidence': annotation.confidence if hasattr(annotation, 'confidence') else 1.0
            })
    
    return all_blocks, full_text

def group_by_lines(blocks, threshold=20):
    """Agrupa bloques de texto por líneas (misma coordenada Y aproximada)"""
    lines = {}
    for block in blocks:
        # Redondear Y para agrupar palabras en la misma línea
        y_group = round(block['y'] / threshold) * threshold
        if y_group not in lines:
            lines[y_group] = []
        lines[y_group].append(block)
    
    # Ordenar cada línea por X
    for y in lines:
        lines[y].sort(key=lambda b: b['x'])
    
    return lines

def detect_matches_from_blocks(blocks, full_text):
    """
    Detecta partidos usando dos estrategias:
    1. Por patrón de cuotas (detección principal)
    2. Por texto 'vs' (fallback)
    """
    lines = group_by_lines(blocks)
    matches = []
    
    # ESTRATEGIA 1: Buscar líneas con 3 números (cuotas)
    odds_pattern = r'[+-]?\d+\.?\d*'  # Captura números como +120, 2.10, -110
    
    for y, line_blocks in lines.items():
        line_text = ' '.join([b['text'] for b in line_blocks])
        
        # Buscar todos los números en la línea
        numbers = re.findall(odds_pattern, line_text)
        
        # Si encontramos 3 o más números, probablemente son cuotas
        if len(numbers) >= 3:
            # Intentar identificar equipos (antes y después de las cuotas)
            # Asumimos formato: [Equipo Local] [Cuota1] [Cuota2] [Cuota3] [Equipo Visitante]
            text_parts = re.split(r'\s+', line_text)
            
            # Encontrar índices de las cuotas
            number_indices = [i for i, part in enumerate(text_parts) if re.match(odds_pattern, part)]
            
            if len(number_indices) >= 3:
                # Todo antes del primer número es equipo local
                local = ' '.join(text_parts[:number_indices[0]]).strip()
                # Los tres números son cuotas
                odds = [text_parts[i] for i in number_indices[:3]]
                # Todo después del tercer número es equipo visitante
                visitante = ' '.join(text_parts[number_indices[2]+1:]).strip()
                
                if local and visitante:
                    matches.append({
                        'local': local,
                        'visitante': visitante,
                        'cuotas': odds,
                        'confianza': 'ALTA',
                        'metodo': 'odds_pattern'
                    })
    
    # ESTRATEGIA 2: Si no encontramos por cuotas, buscar "vs"
    if not matches:
        for line in full_text.split('\n'):
            if ' vs ' in line.lower():
                parts = re.split(r'\s+vs\s+', line, flags=re.IGNORECASE)
                if len(parts) == 2:
                    matches.append({
                        'local': parts[0].strip(),
                        'visitante': parts[1].strip(),
                        'cuotas': ['+100', '+100', '+100'],  # Default
                        'confianza': 'MEDIA',
                        'metodo': 'vs_pattern'
                    })
    
    return matches

def read_ticket_image(uploaded_file):
    """Versión mejorada que lee tanto PC como celular"""
    try:
        # Inicializar cliente de Vision
        client = vision.ImageAnnotatorClient.from_service_account_info(
            dict(st.secrets["google_credentials"])
        )
        
        content = uploaded_file.getvalue()
        image = vision.Image(content=content)
        
        # Detectar tipo de dispositivo
        device = detect_device_type(content)
        st.info(f"📱 Dispositivo detectado: **{device}**")
        
        # Obtener anotaciones de texto
        response = client.text_detection(image=image)
        
        if not response.text_annotations:
            st.warning("No se detectó texto en la imagen")
            return []
        
        # Extraer datos estructurados
        blocks, full_text = extract_structured_data(response.text_annotations)
        
        # Detectar partidos
        matches = detect_matches_from_blocks(blocks, full_text)
        
        # Mostrar debug en Streamlit
        if st.checkbox("🔍 Ver texto detectado (debug)"):
            st.text(full_text[:500] + "...")
            st.json(blocks[:10])  # Mostrar primeros 10 bloques
        
        return matches
        
    except Exception as e:
        st.error(f"Error en OCR: {str(e)}")
        return []