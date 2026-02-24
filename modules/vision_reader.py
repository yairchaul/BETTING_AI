from google.cloud import vision
import streamlit as st

def get_vision_client():
    creds_dict = dict(st.secrets["google_credentials"])
    return vision.ImageAnnotatorClient.from_service_account_info(creds_dict)

def analyze_betting_image(uploaded_file):
    client = get_vision_client()
    content = uploaded_file.read()
    image = vision.Image(content=content)
    
    # Usamos full_text_annotation para obtener precisión símbolo por símbolo
    response = client.document_text_detection(image=image)
    
    raw_data = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                # Unimos el texto del párrafo
                text = "".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                
                # Obtenemos el centro Y (vertical) y X (horizontal)
                vertices = paragraph.bounding_box.vertices
                y_center = sum([v.y for v in vertices]) / 4
                x_center = sum([v.x for v in vertices]) / 4
                
                raw_data.append({"text": text, "y": y_center, "x": x_center})

    if not raw_data:
        return []

    # 1. Ordenar verticalmente para identificar filas
    raw_data.sort(key=lambda item: item['y'])

    # 2. Agrupar en filas (Threshold de 40px para pantallas móviles/web)
    rows = []
    if raw_data:
        current_row = [raw_data[0]]
        for i in range(1, len(raw_data)):
            # Si la diferencia vertical es pequeña, es la misma fila
            if abs(raw_data[i]['y'] - current_row[-1]['y']) < 38:
                current_row.append(raw_data[i])
            else:
                rows.append(current_row)
                current_row = [raw_data[i]]
        rows.append(current_row)

    equipos_finales = []
    # Lista de términos que NO son nombres de equipos
    blacklist = ["empate", "vix", "en vivo", "hoy", "mañana", "apostar", "ver", "live"]

    for row in rows:
        # Ordenar cada fila de izquierda a derecha por X
        row.sort(key=lambda item: item['x'])
        
        # Filtrar solo palabras que parecen nombres de equipos
        # (Sin números, no están en blacklist, longitud > 2)
        clean_elements = []
        for item in row:
            txt = item['text'].strip()
            if (not any(char.isdigit() for char in txt) and 
                txt.lower() not in blacklist and 
                len(txt) > 2):
                clean_elements.append(txt)

        # Si encontramos al menos 2 elementos, asumimos Local y Visitante
        if len(clean_elements) >= 2:
            # En Caliente: [Local, ..., Visitante]
            local = clean_elements[0]
            visitante = clean_elements[-1]
            
            # Evitar duplicados (como cuando lee Stuttgart dos veces en la misma fila)
            if local.lower() != visitante.lower():
                equipos_finales.append(local)
                equipos_finales.append(visitante)

    return equipos_finales
