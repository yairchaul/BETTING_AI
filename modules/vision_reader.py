import re
import streamlit as st
from google.cloud import vision

def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    word_list = []

    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        
        # 1. Extraer palabras con sus cajas de colisión (bounding boxes)
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    text = "".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                    v = paragraph.bounding_box.vertices
                    # Coordenadas promedio
                    avg_y = (v[0].y + v[2].y) / 2
                    avg_x = (v[0].x + v[2].x) / 2
                    word_list.append({"text": text, "x": avg_x, "y": avg_y})
    except Exception as e:
        st.error(f"Error Vision: {e}")
        return []

    # 2. Agrupar por FILAS (Y similares) con una tolerancia mayor (30-40px)
    # porque los nombres de los equipos suelen estar en dos renglones
    word_list.sort(key=lambda w: w["y"])
    rows = []
    if word_list:
        current_row = [word_list[0]]
        for i in range(1, len(word_list)):
            # Si la diferencia en Y es pequeña, es la misma fila de apuesta
            if abs(word_list[i]["y"] - current_row[-1]["y"]) < 45: 
                current_row.append(word_list[i])
            else:
                rows.append(current_row)
                current_row = [word_list[i]]
        rows.append(current_row)

    final_matches = []

    # 3. Procesar cada fila detectada
    for row in rows:
        # Separar elementos de la fila por su posición X (Izquierda=Equipos, Derecha=Momios)
        row.sort(key=lambda w: w["x"])
        
        # Filtramos momios: texto que empieza con + o - y tiene números
        odds = [w["text"] for w in row if re.match(r'^[+-]\d{2,}$', w["text"])]
        
        # Filtramos nombres: texto que NO sea fecha, ni momio, ni el "+43"
        names = []
        for w in row:
            t = w["text"]
            # Ignorar si es momio, si es "+43", o si parece fecha (28, Feb, 03:00)
            if not re.match(r'^[+-]\d+$', t) and \
               not re.match(r'^\+\d+$', t) and \
               not re.match(r'^\d{2}$', t) and \
               t not in ["Feb", "Mar", "Jan"] and \
               ":" not in t:
                names.append(t)

        # Si tenemos al menos 2 nombres y 3 momios, es un partido válido
        if len(odds) >= 3 and len(names) >= 2:
            # Los nombres suelen venir en orden: Equipo 1, Equipo 2
            # Unimos los nombres por si el equipo tiene varias palabras (ej. Brisbane Strikers)
            mid = len(names) // 2
            home = " ".join(names[:mid])
            away = " ".join(names[mid:])
            
            final_matches.append({
                "home": home,
                "away": away,
                "odds": odds[:3] # 1, X, 2
            })

    return final_matches
