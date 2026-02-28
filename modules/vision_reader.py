import re
import streamlit as st
import pandas as pd
from google.cloud import vision

def clean_team_name(text_list):
    """Limpia ruidos específicos como fechas, horas y contadores (+43)"""
    meses = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    cleaned = []
    for t in text_list:
        t_low = t.lower()
        # Ignorar si es: momio (+123), contador (+43), hora (03:00), mes o día numérico
        if re.match(r'^[+-]\d+$', t): continue
        if ":" in t: continue
        if t_low in meses: continue
        if t.isdigit() and int(t) <= 31: continue
        cleaned.append(t)
    return cleaned

def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    all_words = []

    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    # Unimos símbolos para mantener nombres compuestos (ej. Brisbane Strikers)
                    text = "".join([s.text for s in paragraph.words[0].symbols])
                    # Si el párrafo tiene varias palabras, las unimos
                    full_text = " ".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                    v = paragraph.bounding_box.vertices
                    all_words.append({
                        "text": full_text,
                        "x": (v[0].x + v[2].x) / 2,
                        "y": (v[0].y + v[2].y) / 2
                    })
    except Exception as e:
        st.error(f"Error de Vision: {e}")
        return []

    # 1. Agrupar por filas usando Y (tolerancia para nombres en dos líneas)
    all_words.sort(key=lambda w: w["y"])
    rows = []
    if all_words:
        current_row = [all_words[0]]
        for i in range(1, len(all_words)):
            if abs(all_words[i]["y"] - current_row[-1]["y"]) < 60: # Margen para captar ambos equipos
                current_row.append(all_words[i])
            else:
                rows.append(current_row)
                current_row = [all_words[i]]
        rows.append(current_row)

    matches = []
    for row in rows:
        row.sort(key=lambda w: w["x"]) # Ordenar de izquierda a derecha
        
        # Extraer momios (buscamos exactamente 3 que cumplan el formato +XXX o -XXX)
        odds = [w["text"] for w in row if re.match(r'^[+-]\d{3}$', w["text"])]
        
        if len(odds) >= 3:
            # Extraer nombres ignorando los momios ya identificados y la basura
            potential_names = [w["text"] for w in row if w["text"] not in odds]
            clean_list = clean_team_name(potential_names)
            
            if len(clean_list) >= 2:
                # El primer elemento suele ser el Local y el segundo el Visitante 
                # debido al orden de lectura de Vision en estos bloques
                matches.append({
                    "Local": clean_list[0],
                    "Visitante": clean_list[1],
                    "1": odds[0],
                    "X": odds[1],
                    "2": odds[2]
                })

    return matches

# --- Streamlit UI ---
st.title("Extraer Apuestas")
file = st.file_uploader("Subir imagen", type=["png", "jpg"])

if file:
    res = analyze_betting_image(file)
    if res:
        st.table(pd.DataFrame(res))
    else:
        st.info("No se encontraron partidos. Asegúrate de que los momios (+/-) sean visibles.")
