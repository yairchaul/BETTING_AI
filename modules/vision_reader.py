import re

def analyze_betting_image(archivo):
    """
    Extracción global: Captura bloques de texto (equipos) y bloques de números (momios).
    No depende de listas de equipos.
    """
    # Simulamos el texto bruto que viene del OCR
    raw_text = "Oita Trinita vs Reilac Shiga FC +120 +240 +210 Kirivong vs Svay Rieng +1500 +600 -1200"

    # Captura nombres largos (incluyendo FC, United, City, etc.)
    pattern_teams = r'([A-Z][a-zñáéíóú]+(?:\s[A-Z][a-zñáéíóúFCUnite]+)*)'
    pattern_odds = r'([+-]\d{2,4})'

    teams = re.findall(pattern_teams, raw_text)
    odds = re.findall(pattern_odds, raw_text)

    matches = []
    # Emparejamiento por proximidad: cada 2 equipos, 3 momios (1, X, 2)
    for i in range(0, len(teams) - 1, 2):
        idx_o = (i // 2) * 3
        if idx_o + 2 < len(odds):
            matches.append({
                "home": teams[i].strip(),
                "away": teams[i+1].strip(),
                "home_odd": odds[idx_o],
                "draw_odd": odds[idx_o+1],
                "away_odd": odds[idx_o+2]
            })
    return matches, f"Detectados {len(matches)} partidos analizados globalmente."
