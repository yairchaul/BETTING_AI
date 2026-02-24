import re
import io
import streamlit as st
from google.cloud import vision
from PIL import Image, ImageDraw

def is_odd(text: str) -> bool:
    cleaned = re.sub(r'\s+', '', text.strip())
    return bool(re.match(r'^[+-]?\d{2,4}$', cleaned))

def detect_market_type(texts: list) -> str:
    text_str = " ".join(texts).lower()
    if any(x in text_str for x in ["over", "under", "más de", "menos de"]):
        for t in texts:
            if re.search(r'2\.5|1\.5|3\.5|0\.5', t):
                return f"Over/Under {t}"
    if "ambos" in text_str or "btts" in text_str:
        return "BTTS"
    return "1X2"

def parse_row(texts: list) -> dict | None:
    market = detect_market_type(texts)
    
    if market == "1X2":
        if "Empate" not in texts:
            return None
        i = 0
        home_parts = []
        while i < len(texts) and not is_odd(texts[i]) and texts[i] != "Empate":
            home_parts.append(texts[i])
            i += 1
        home = " ".join(home_parts).strip()
        
        if i >= len(texts) or not is_odd(texts[i]): return None
        home_odd = texts[i]; i += 1
        
        if i >= len(texts) or texts[i] != "Empate": return None
        i += 1
        
        if i >= len(texts) or not is_odd(texts[i]): return None
        draw_odd = texts[i]; i += 1
        
        away_parts = []
        while i < len(texts) and not is_odd(texts[i]):
            away_parts.append(texts[i])
            i += 1
        away = " ".join(away_parts).strip()
        
        return {
            "market": "1X2",
            "home": home,
            "home_odd": home_odd,
            "draw_odd": draw_odd,
            "away": away,
            "away_odd": texts[i] if i < len(texts) and is_odd(texts[i]) else None
        }
    
    elif "Over/Under" in market:
        # Ejemplo: "Over 2.5" + odd
        line = re.search(r'(\d+\.?\d*)', " ".join(texts)).group(1) if re.search(r'\d+\.?\d*', " ".join(texts)) else "2.5"
        odd = next((t for t in texts if is_odd(t)), None)
        return {
            "market": market,
            "line": line,
            "odd": odd,
            "type": "Over" if "over" in " ".join(texts).lower() else "Under"
        }
    
    return None

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
                        "height": max_y - min_y
                    })
    
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
        if len(row_words) < 3: continue
        row_words.sort(key=lambda w: w["x"])
        texts = [w["text"] for w in row_words]
        debug_rows.append(texts)
        
        match = parse_row(texts)
        if match:
            matches.append(match)
    
    with st.expander("🔍 DEBUG OCR - Filas detectadas", expanded=False):
        for i, texts in enumerate(debug_rows):
            st.write(f"Fila {i+1}: {texts}")
        st.success(f"✅ {len(matches)} mercados detectados (1X2 + Over/Under)")
    
    return matches
