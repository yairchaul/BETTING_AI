# Modificación en modules/vision_reader.py para no restringir mercados
def parse_row(texts: list) -> dict | None:
    odds = [t for t in texts if is_odd(t)]
    if not odds: return None
    
    # Extraemos equipos ignorando los momios y palabras cortas
    teams = [t for t in texts if not is_odd(t) and len(t) > 3]
    
    return {
        "home": teams[0] if len(teams) > 0 else "Unknown",
        "away": teams[1] if len(teams) > 1 else "Unknown",
        "detected_odds": odds, # Pasamos todos los momios encontrados
        "raw_context": " ".join(texts)
    }
