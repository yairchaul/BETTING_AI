# Modificación estratégica en modules/vision_reader.py
def parse_row(texts: list) -> dict | None:
    odds = [t for t in texts if is_odd(t)]
    if not odds: return None

    text_str = " ".join(texts).lower()
    
    # Retornamos un objeto genérico con TODO el texto capturado para que el Cerebro decida
    return {
        "raw_text": text_str,
        "full_row": texts,
        "detected_odds": odds,
        # Intentamos identificar equipos por posición (palabras iniciales)
        "potential_teams": [t for t in texts if not is_odd(t) and len(t) > 3][:2]
    }
