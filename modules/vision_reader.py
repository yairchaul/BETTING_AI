import re
import streamlit as st
from google.cloud import vision

def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    word_list = []

    try:
        # Configuración de cliente (asegúrate de que st.secrets esté bien)
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        
        # 1. Extraer palabras con sus coordenadas
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    # Unimos símbolos para formar palabras completas
                    word_text = "".join([s.text for s in paragraph.words[0].symbols]) 
                    # Usamos el promedio de Y para situar la línea
                    vertices = paragraph.bounding_box.vertices
                    avg_y = sum(v.y for v in vertices) / 4
                    avg_x = sum(v.x for v in vertices) / 4
                    word_list.append({"text": " ".join(["".join([s.text for s in w.symbols]) for w in paragraph.words]), "x": avg_x, "y": avg_y})
    except Exception as e:
        st.error(f"Error: {e}")
        return []

    # 2. Agrupar por "Líneas" (Y similares)
    # Tolerancia de 15-20 píxeles para considerar que están en la misma fila
    word_list.sort(key=lambda w: w["y"])
    lines = []
    if word_list:
        current_line = [word_list[0]]
        for i in range(1, len(word_list)):
            if abs(word_list[i]["y"] - current_line[-1]["y"]) < 15:
                current_line.append(word_list[i])
            else:
                current_line.sort(key=lambda w: w["x"]) # Ordenar de izquierda a derecha
                lines.append(current_line)
                current_line = [word_list[i]]
        lines.append(current_line)

    # 3. Filtrar y Estructurar
    matches = []
    for line in lines:
        text_line = " ".join([w["text"] for w in line])
        
        # Buscamos momios (números con + o - y 3 dígitos)
        odds = re.findall(r'[+-]\d{3,}', text_line)
        
        if len(odds) >= 3:
            # Si hay 3 momios, lo que esté a la izquierda suelen ser los equipos
            # Limpiamos el texto para quitar la fecha y el "+43"
            clean_text = re.sub(r'\+\s*\d+', '', text_line) # Quita +43
            clean_text = re.sub(r'\d{1,2}\s*[A-Za-z]{3}\s*\d{2}:\d{2}', '', clean_text) # Quita fecha
            clean_text = clean_text.replace(odds[0], "").replace(odds[1], "").replace(odds[2], "").strip()
            
            # Intentar separar local y visitante (usualmente por saltos de línea o espacios largos)
            # En esa imagen, los nombres están uno sobre otro o separados
            parts = [p.strip() for p in clean_text.split("  ") if len(p.strip()) > 2]
            
            matches.append({
                "equipos": clean_text,
                "home_odd": odds[0],
                "draw_odd": odds[1],
                "away_odd": odds[2]
            })

    return matches
