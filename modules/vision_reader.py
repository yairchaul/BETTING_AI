from google.cloud import vision
import streamlit as st

def get_vision_client():
    creds_dict = dict(st.secrets["google_credentials"])
    return vision.ImageAnnotatorClient.from_service_account_info(creds_dict)

def analyze_betting_image(uploaded_file):
    client = get_vision_client()
    content = uploaded_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    
    raw_data = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                text = "".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                v = paragraph.bounding_box.vertices
                y_center = sum([p.y for p in v]) / 4
                x_center = sum([p.x for p in v]) / 4
                raw_data.append({"text": text, "y": y_center, "x": x_center})

    if not raw_data: return []

    # 1. Ordenar por altura (Y)
    raw_data.sort(key=lambda x: x['y'])

    # 2. Agrupar por filas (Umbral de 25px para ser muy precisos)
    rows = []
    if raw_data:
        current_row = [raw_data[0]]
        for i in range(1, len(raw_data)):
            if abs(raw_data[i]['y'] - current_row[-1]['y']) < 25:
                current_row.append(raw_data[i])
            else:
                rows.append(current_row)
                current_row = [raw_data[i]]
        rows.append(current_row)

    equipos_finales = []
    blacklist = ["empate", "vix", "en vivo", "apostar", "ver", "hoy", "mañana", "liga", "mx"]

    for row in rows:
        # Ordenar cada fila de izquierda a derecha (X)
        row.sort(key=lambda x: x['x'])
        
        # Filtrar solo nombres reales
        clean_row = []
        for item in row:
            t = item['text'].strip()
            # Quitamos momios (números), basura y palabras de liga
            if not any(char.isdigit() for char in t) and t.lower() not in blacklist and len(t) > 2:
                clean_row.append(t)

        # REGLA DE ORO: Solo aceptamos la fila si detectamos un Local y un Visitante 
        # claramente separados (uno al principio y otro al final de la línea)
        if len(clean_row) >= 2:
            local = clean_row[0]
            visitante = clean_row[-1]
            if local.lower() != visitante.lower():
                equipos_finales.append(local)
                equipos_finales.append(visitante)

    return equipos_finales
