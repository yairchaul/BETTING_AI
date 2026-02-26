import re

def clean_name(name):
    """Limpia ruidos del OCR y sufijos regionales."""
    # Elimina caracteres extraños
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
    
    # Lista de sufijos a limpiar
    suffixes = [' SE', ' FC', ' ES', ' UNPFM', ' United', ' U20', ' CD', ' Junior']
    for s in suffixes:
        name = re.sub(rf'{s}$', '', name, flags=re.IGNORECASE)
    
    return name.strip()

def get_team_stats(home, away):
    """
    Obtiene estadísticas basadas en nombres limpios.
    """
    home_clean = clean_name(home)
    away_clean = clean_name(away)
    
    # Simulación de datos para los últimos 5 partidos
    # Aquí puedes conectar tu API de estadísticas
    return {
        'home_goals_avg': 1.6, 
        'away_goals_avg': 1.1,
        'home_form': 0.8,
        'away_form': 0.4,
        'home_name': home_clean,
        'away_name': away_clean
    }
