from google.cloud import vision
import streamlit as st

def get_vision_client():
    creds_dict = dict(st.secrets["google_credentials"])
    return vision.ImageAnnotatorClient.from_service_account_info(creds_dict)

def analyze_betting_image(uploaded_file):
    client = get_vision_client()
    content = uploaded_file.read()
    image = vision.Image(content=content)
    
    # Usamos document_text_detection para mejor lectura de tablas
    response = client.document_text_detection(image=image)
    
    words_data = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                text = "".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                # Centro vertical del bloque
                y_center = sum([v.y for v in paragraph.bounding_box.vertices]) / 4
                words_data.append({"text": text, "y": y_center})

    if not words_data:
        return []

    # 1. Ordenar por altura
    words_data.sort(key=lambda x: x['y'])

    # 2. Agrupar en filas usando un umbral más amplio (40px suele ser el estándar de filas en móvil)
    rows = []
    current_row = [words_data[0]]
    
    for i in range(1, len(words_data)):
        # Si la palabra está a menos de 35 píxeles de la anterior, es la misma fila
        if abs(words_data[i]['y'] - current_row[-1]['y']) < 35:
            current_row.append(words_data[i])
        else:
            rows.append(current_row)
            current_row = [words_data[i]]
    rows.append(current_row)

    equipos_finales = []
    # Palabras prohibidas que ensucian la detección de equipos
    blacklist = ["empate", "vix", "en", "vivo", "hoy", "mañana", "apostar", "ver"]

    for row in rows:
        # Extraer solo el texto y limpiar
        textos_fila = [item['text'] for item in row]
        
        # Filtro: Ignorar números (momios), "Empate" y palabras de la blacklist
        clean_row = []
        for t in textos_fila:
            # Si tiene números o es palabra prohibida, ignorar
            if any(char.isdigit() for char in t) or t.lower() in blacklist:
                continue
            if len(t) > 2: # Evitar basura de 1 o 2 letras
                clean_row.append(t)

        # En la interfaz de Caliente, el primer texto es Local y el último es Visitante
        if len(clean_row) >= 2:
            equipos_finales.append(clean_row[0])  # Local
            equipos_finales.append(clean_row[-1]) # Visitante

    return equipos_finales
