from google.cloud import vision
import streamlit as st

def get_vision_client():
    creds_dict = dict(st.secrets["google_credentials"])
    return vision.ImageAnnotatorClient.from_service_account_info(creds_dict)

def analyze_betting_image(uploaded_file):
    client = get_vision_client()
    content = uploaded_file.read()
    image = vision.Image(content=content)
    
    # Detección de texto denso para obtener coordenadas exactas
    response = client.document_text_detection(image=image)
    
    words_data = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                text = "".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                vertices = paragraph.bounding_box.vertices
                # Calculamos el centro vertical (Y) y horizontal (X)
                y_center = sum([v.y for v in vertices]) / 4
                x_center = sum([v.x for v in vertices]) / 4
                words_data.append({"text": text, "y": y_center, "x": x_center})

    if not words_data:
        return []

    # 1. Ordenar por altura (Y)
    words_data.sort(key=lambda x: x['y'])

    # 2. Agrupar en filas (Threshold de 35px para evitar mezclar partidos)
    rows = []
    current_row = [words_data[0]]
    for i in range(1, len(words_data)):
        if abs(words_data[i]['y'] - current_row[-1]['y']) < 35:
            current_row.append(words_data[i])
        else:
            rows.append(current_row)
            current_row = [words_data[i]]
    rows.append(current_row)

    equipos_finales = []
    blacklist = ["empate", "vix", "en vivo", "hoy", "apostar", "ver", "mañana", "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

    for row in rows:
        # Ordenar elementos de la fila de IZQUIERDA a DERECHA (X)
        row.sort(key=lambda x: x['x'])
        
        # Filtrar solo palabras que no tengan números (para quitar momios como +120)
        clean_elements = []
        for item in row:
            txt = item['text'].strip()
            # Si no tiene números, no es "Empate" y es suficientemente largo
            if (not any(char.isdigit() for char in txt) and 
                txt.lower() not in blacklist and 
                len(txt) > 2):
                clean_elements.append(txt)

        # SI LA FILA ES UN PARTIDO: tendrá al menos el Local y el Visitante
        if len(clean_elements) >= 2:
            # El primero es el que está más a la izquierda (Local)
            # El último es el que está más a la derecha (Visitante)
            local = clean_elements[0]
            visitante = clean_elements[-1]
            
            # Verificación de seguridad: que no sea el mismo nombre
            if local.lower() != visitante.lower():
                equipos_finales.append(local)
                equipos_finales.append(visitante)

    return equipos_finales
