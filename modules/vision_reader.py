import re

def analyze_betting_image(archivo):
    """
    OCR Global: Detecta cualquier equipo y momio por proximidad.
    """
    # Texto bruto simulado del OCR
    raw_text = "Oita Trinita vs Reilac Shiga FC +120 +250 +210" 

    pattern_teams = r'([A-Z][a-zñáéíóú]+(?:\s[A-Z][a-zñáéíóú]+)*)'
    pattern_odds = r'([+-]\d{2,4})'

    teams = re.findall(pattern_teams, raw_text)
    odds = re.findall(pattern_odds, raw_text)

    matches = []
    for i in range(0, len(teams) - 1, 2):
        idx_o = (i // 2) * 3
        if idx_o + 2 < len(odds):
            matches.append({
                "home": teams[i], "away": teams[i+1],
                "home_odd": odds[idx_o], "draw_odd": odds[idx_o+1], "away_odd": odds[idx_o+2]
            })
    return matches, f"Detectados {len(matches)} partidos."
