import re

def analyze_betting_image(archivo):
    """
    EXTRACCIÓN GLOBAL: No depende de nombres específicos.
    Busca patrones de texto y momios en toda la imagen y los agrupa por proximidad.
    """
    # 1. El OCR debe entregar el texto bruto (aquí simulado)
    # Este proceso ahora es agnóstico: cualquier palabra con Mayúscula es un equipo potencial.
    raw_text = "Cualquier Equipo A vs Cualquier Equipo B +120 -110 +300" 

    # Patrón para momios americanos (+150, -200, etc)
    pattern_odds = r'([+-]\d{3,4})'
    # Patrón para nombres de equipos (Palabras que empiezan con Mayúscula)
    pattern_teams = r'([A-Z][a-zñáéíóú]+(?:\s[A-Z][a-zñáéíóú]+)*)'

    all_odds = re.findall(pattern_odds, raw_text)
    all_teams = re.findall(pattern_teams, raw_text)

    matches = []
    
    # Emparejamiento por estructura de bloques (Global)
    for i in range(0, len(all_teams) - 1, 2):
        idx_odd = (i // 2) * 3
        if idx_odd + 2 < len(all_odds):
            matches.append({
                "home": all_teams[i],
                "away": all_teams[i+1],
                "home_odd": all_odds[idx_odd],
                "draw_odd": all_odds[idx_odd+1],
                "away_odd": all_odds[idx_odd+2]
            })
    
    return matches, f"Global: {len(matches)} partidos detectados."
