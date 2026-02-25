# modules/vision_reader.py - Lector global de tickets (imagen o texto pegado)
import re

def analizar_ticket(texto_raw):
    """
    Detecta partidos y momios de forma 100% global.
    Funciona con cualquier liga y formato de Caliente.mx.
    """
    lines = texto_raw.split('\n')
    matches = []

    for line in lines:
        # Patrón global: equipos (mayúsculas + palabras) + momios (+/- números)
        team_pattern = r'([A-Z][A-Za-zñáéíóú\s]+?)\s+(?=[+-]|\d)'
        odd_pattern = r'([+-]?\d{3,4})'

        teams = re.findall(team_pattern, line)
        odds = re.findall(odd_pattern, line)

        if len(teams) >= 2 and len(odds) >= 3:
            home = teams[0].strip()
            away = teams[1].strip()
            # Tomamos los 3 momios principales (1, X, 2)
            home_odd = odds[0]
            draw_odd = odds[1] if len(odds) > 1 else '+999'
            away_odd = odds[2] if len(odds) > 2 else '+999'

            matches.append({
                "home": home,
                "away": away,
                "home_odd": home_odd,
                "draw_odd": draw_odd,
                "away_odd": away_odd,
                "raw": line.strip()
            })

    return matches
