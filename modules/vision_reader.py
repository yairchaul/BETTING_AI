# modules/vision_reader.py - Lector global de tickets con OCR real
import easyocr
import re
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO)

def analizar_ticket(archivo=None, texto_manual=None):
    """
    EXTRACCIÓN GLOBAL: No depende de nombres específicos.
    1. Si se sube imagen → OCR con easyocr
    2. Si se pega texto → lo usa directamente
    3. Detecta equipos y momios por patrones y proximidad
    """
    raw_text = ""

    if archivo is not None:
        try:
            # Leer imagen subida
            img_bytes = archivo.read()
            img = Image.open(io.BytesIO(img_bytes))
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Inicializar lector OCR (español + inglés)
            reader = easyocr.Reader(['es', 'en'], gpu=False)
            result = reader.readtext(img, detail=0, paragraph=False)
            
            # Unir todo el texto detectado
            raw_text = ' '.join(result)
            logging.info(f"Texto extraído por OCR: {raw_text[:200]}...")
        except Exception as e:
            logging.error(f"Error en OCR: {e}")
            raw_text = ""
    elif texto_manual:
        raw_text = texto_manual

    if not raw_text.strip():
        return [], "No se pudo extraer texto de la imagen o del campo manual."

    # -----------------------
    # Patrón global y agnóstico
    # -----------------------
    # Momios americanos: +150, -200, etc.
    pattern_odds = r'([+-]\d{3,4})'
    
    # Equipos: palabras que empiezan con mayúscula, permiten espacios
    pattern_teams = r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)'

    all_odds = re.findall(pattern_odds, raw_text)
    all_teams = re.findall(pattern_teams, raw_text)

    matches = []

    # Vinculación por bloques (asumimos estructura 2 equipos → 3 momios)
    i = 0
    while i < len(all_teams) - 1:
        # Intentar tomar 2 equipos consecutivos
        home = all_teams[i].strip()
        away = all_teams[i + 1].strip()
        
        # Buscar 3 momios cercanos en el texto completo
        start_idx = raw_text.find(home)
        end_idx = raw_text.find(away, start_idx) + len(away)
        bloque = raw_text[start_idx:end_idx + 100]  # ventana después del away
        
        odds_bloque = re.findall(pattern_odds, bloque)
        
        if len(odds_bloque) >= 3:
            matches.append({
                "home": home,
                "away": away,
                "home_odd": odds_bloque[0],
                "draw_odd": odds_bloque[1],
                "away_odd": odds_bloque[2],
                "raw_block": bloque[:100] + "..."
            })
            i += 2  # Saltar los dos equipos usados
        else:
            i += 1  # Intentar siguiente

    if matches:
        return matches, f"Detectados {len(matches)} partidos de forma global."
    else:
        return [], "No se detectaron momios válidos en el texto extraído."
