import re
import streamlit as st
from google.cloud import vision
import pandas as pd

def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    word_list = []

    try:
        # Configuración de Google Vision
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        
        if not response.full_text_annotation:
            return []

        # 1. Extraer palabras con coordenadas
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    # Unimos los símbolos para formar la palabra/frase del párrafo
                    text = "".join(["".join([s.text for s in w.symbols]) for w in paragraph.words])
                    v = paragraph.bounding_box.vertices
                    avg_y = (v[0].y + v[2].y) / 2
                    avg_x = (v[0].x + v[2].x) / 2
                    word_list.append({"text": text, "x": avg_x, "y": avg_y})
    except Exception as e:
        st.error(f"Error con Google Vision: {e}")
        return []

    # 2. Agrupar por FILAS (Tolerancia Y de 45px para captar ambos equipos)
    word_list.sort(key=lambda w: w["y"])
    rows = []
    if word_list:
        current_row = [word_list[0]]
        for i in range(1, len(word_list)):
            if abs(word_list[i]["y"] - current_row[-1]["y"]) < 45: 
                current_row.append(word_list[i])
            else:
                rows.append(current_row)
                current_row = [word_list[i]]
        rows.append(current_row)

    data_para_tabla = []

    # 3. Limpiar y estructurar cada fila
    for row in rows:
        # Ordenar de izquierda a derecha
        row.sort(key=lambda w: w["x"])
        
        # Identificar momios (empiezan con + o - y tienen al menos 3 dígitos)
        odds = [w["text"] for w in row if re.match(r'^[+-]\d{3}$', w["text"])]
        
        # Identificar nombres de equipos (filtramos basura: fechas, horas, "+43")
        team_parts = []
        for w in row:
            t = w["text"]
            # Excluimos si es: momio, "+XX", fecha (28 Feb), o hora (03:00)
            if not re.match(r'^[+-]\d+$', t) and \
               not re.match(r'^\+\d+$', t) and \
               not re.match(r'^\d{2}$', t) and \
               t not in ["Feb", "Mar", "Jan", "Feb", "28"] and \
               ":" not in t:
                team_parts.append(t)

        # Si encontramos 3 momios, procesamos la fila
        if len(odds) >= 3 and len(team_parts) >= 2:
            # Dividimos los nombres detectados a la mitad para Local vs Visitante
            mid = len(team_parts) // 2
            home_team = " ".join(team_parts[:mid])
            away_team = " ".join(team_parts[mid:])
            
            data_para_tabla.append({
                "Local": home_team,
                "Visitante": away_team,
                "1 (Local)": odds[0],
                "X (Empate)": odds[1],
                "2 (Visita)": odds[2]
            })

    return data_para_tabla

# --- INTERFAZ DE STREAMLIT ---
st.title("OCR de Apuestas de Fútbol")
uploaded_file = st.file_uploader("Sube la captura de pantalla", type=["png", "jpg", "jpeg"])

if uploaded_file:
    with st.spinner('Analizando imagen...'):
        resultados = analyze_betting_image(uploaded_file)
        
    if resultados:
        st.success(f"Se detectaron {len(resultados)} partidos.")
        df = pd.DataFrame(resultados)
        st.table(df) # Muestra una tabla limpia
    else:
        st.warning("No se pudieron extraer partidos. Asegúrate de que los momios (+/- XXX) sean visibles.")
