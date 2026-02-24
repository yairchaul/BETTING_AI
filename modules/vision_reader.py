from google.cloud import vision
import streamlit as st

def get_vision_client():
    creds_dict = dict(st.secrets["google_credentials"])
    return vision.ImageAnnotatorClient.from_service_account_info(creds_dict)

def analyze_betting_image(uploaded_file):
    client = get_vision_client()
    content = uploaded_file.read()
    image = vision.Image(content=content)
    
    # Usamos document_text_detection para obtener coordenadas densas
    response = client.document_text_detection(image=image)
    
    lines = []
    # Extraer texto con su posición Y (vertical)
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                text = "".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                # Tomar el promedio de Y de los 4 vértices del bloque
                y_coord = sum([v.y for v in paragraph.bounding_box.vertices]) / 4
                lines.append({"text": text, "y": y_coord})

    # 1. Ordenar de arriba hacia abajo
    lines.sort(key=lambda x: x['y'])

    # 2. Agrupar por filas (umbral de 20-30 píxeles de diferencia)
    grouped_rows = []
    if not lines: return []

    current_row = [lines[0]]
    for i in range(1, len(lines)):
        if abs(lines[i]['y'] - current_row[-1]['y']) < 25: 
            current_row.append(lines[i])
        else:
            grouped_rows.append(current_row)
            current_row = [lines[i]]
    grouped_rows.append(current_row)

    # 3. Filtrar solo nombres de equipos
    # Ignoramos momios (+123), "Empate" y símbolos de candado
    equipos_finales = []
    ignore_list = ["Empate", "vix", "en vivo", "hoy"]
    
    for row in grouped_rows:
        textos_fila = [item['text'] for item in row]
        # Limpiamos momios y términos basura
        clean_row = [t for t in textos_fila if not any(c.isdigit() for c in t) and t not in ignore_list]
        
        if len(clean_row) >= 2:
            # Tomamos el primero (Local) y el último (Visitante) de esa fila
            equipos_finales.append(clean_row[0])
            equipos_finales.append(clean_row[-1])

    return equipos_finales
