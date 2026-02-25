import re

def analyze_betting_image(archivo):
    """
    Procesa el ticket de forma global. 
    Busca patrones de momios (+/- seguido de números) y nombres de equipos 
    sin restringirse a una base de datos estática.
    """
    # 1. Simulación de OCR (aquí recibes el string completo de la imagen)
    # El objetivo es que el OCR no segmente, sino que entregue el "chorizo" de texto.
    raw_text = "Meisatla Lungleng FC +110 +255 +180 Kirivong Svan Rieng +2000 +580 -1200" 

    # 2. Patrones globales
    # Buscamos cualquier cosa que parezca un momio americano
    pattern_odds = r'([+-]\d{3,4})'
    # Buscamos bloques de texto que parezcan nombres (Palabras con Mayúsculas)
    pattern_teams = r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)'

    all_odds = re.findall(pattern_odds, raw_text)
    all_teams = re.findall(pattern_teams, raw_text)

    matches = []
    
    # 3. Lógica de Vinculación Global (Cascada de Emparejamiento)
    # Por cada 2 equipos encontrados, intentamos extraer los siguientes 3 momios (1 X 2)
    for i in range(0, len(all_teams) - 1, 2):
        try:
            # Calculamos el índice base de los momios para este par de equipos
            # Si es el primer par de equipos, busca los primeros 3 momios, y así...
            idx_odd = (i // 2) * 3
            
            if idx_odd + 2 < len(all_odds):
                game = {
                    "home": all_teams[i],
                    "away": all_teams[i+1],
                    "home_odd": all_odds[idx_odd],    # Momio Local
                    "draw_odd": all_odds[idx_odd+1],  # Momio Empate
                    "away_odd": all_odds[idx_odd+2]   # Momio Visita
                }
                matches.append(game)
        except Exception:
            continue

    # Si no se detectó nada, enviamos un log de debug para el usuario
    debug_msg = f"Detectados: {len(all_teams)} equipos y {len(all_odds)} momios."
    
    return matches, debug_msg
