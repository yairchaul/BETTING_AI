import re
import io
import streamlit as st
from google.cloud import vision
from PIL import Image, ImageDraw

def is_odd(text: str) -> bool:
    cleaned = re.sub(r'\s+', '', text.strip())
    return bool(re.match(r'^[+-]?\d{2,4}$', cleaned))

def parse_row(texts: list) -> dict | None:
    if "Empate" not in texts:
        return None
    i = 0
    # Home team (1-4 palabras)
    home_parts = []
    while i < len(texts) and not is_odd(texts[i]) and texts[i] != "Empate":
        home_parts.append(texts[i])
        i += 1
    home = " ".join(home_parts).strip()
    
    if i >= len(texts) or not is_odd(texts[i]): return None
    home_odd = texts[i]; i += 1
    
    if i >= len(texts) or texts[i] != "Empate": return None
    i += 1  # skip Empate
    
    if i >= len(texts) or not is_odd(texts[i]): return None
    draw_odd = texts[i]; i += 1
    
    # Away team
    away_parts = []
    while i < len(texts) and not is_odd(texts[i]):
        away_parts.append(texts[i])
        i += 1
    away = " ".join(away_parts).strip()
    
    away_odd = texts[i] if i < len(texts) and is_odd(texts[i]) else None
    
    # Validaciones fuertes
    if not home or not away or home == away or len(home) < 3 or len(away) < 3:
        return None
    
    return {
        "home": home,
        "home_odd": home_odd,
        "draw_odd": draw_odd,
        "away": away,
        "away_odd": away_odd,
        "market": "1X2"  # futuro: detectar Over/Under automáticamente
    }

def analyze_betting_image(uploaded_file):
    content = uploaded_file.getvalue()
    client = vision.ImageAnnotatorClient.from_service_account_info(
        dict(st.secrets["google_credentials"])
    )
    image = vision.Image(content=content)
    
    response = client.document_text_detection(image=image)
    
    word_list = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = ''.join(s.text for s in word.symbols).strip()
                    if len(word_text) < 2: continue
                    
                    v = word.bounding_box.vertices
                    min_x = min(vv.x for vv in v)
                    max_x = max(vv.x for vv in v)
                    min_y = min(vv.y for vv in v)
                    max_y = max(vv.y for vv in v)
                    
                    word_list.append({
                        "text": word_text,
                        "x": (min_x + max_x)/2,
                        "y": (min_y + max_y)/2,
                        "height": max_y - min_y,
                        "min_x": min_x, "max_x": max_x,
                        "min_y": min_y, "max_y": max_y
                    })
    
    if not word_list:
        return []
    
    # ROW GROUPING DINÁMICO (funciona en cualquier resolución)
    word_list.sort(key=lambda w: w["y"])
    heights = [w["height"] for w in word_list]
    median_height = sorted(heights)[len(heights)//2] if heights else 30
    row_threshold = median_height * 1.8
    
    rows = []
    current_row = [word_list[0]]
    for w in word_list[1:]:
        if abs(w["y"] - current_row[-1]["y"]) < row_threshold:
            current_row.append(w)
        else:
            rows.append(current_row)
            current_row = [w]
    rows.append(current_row)
    
    matches = []
    debug_rows = []
    
    for row_words in rows:
        if len(row_words) < 5: continue
        row_words.sort(key=lambda w: w["x"])
        texts = [w["text"] for w in row_words]
        debug_rows.append(texts)
        
        match = parse_row(texts)
        if match:
            matches.append(match)
    
    # DEBUG VISUAL (imprescindible para cualquier liga)
    with st.expander("🔍 DEBUG OCR - Filas detectadas", expanded=False):
        for i, texts in enumerate(debug_rows):
            st.write(f"Fila {i+1}: {texts}")
        st.success(f"✅ {len(matches)} partidos estructurados detectados")
    
    # Imagen anotada (opcional pero brutal para debug)
    if st.checkbox("Ver bounding boxes por fila"):
        img = Image.open(io.BytesIO(content))
        draw = ImageDraw.Draw(img)
        colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0)]
        for idx, row in enumerate(rows):
            color = colors[idx % len(colors)]
            for w in row:
                draw.rectangle([w["min_x"], w["min_y"], w["max_x"], w["max_y"]], 
                             outline=color, width=3)
        st.image(img, caption="Debug visual - cada color = una fila", use_column_width=True)
    
    return matches
