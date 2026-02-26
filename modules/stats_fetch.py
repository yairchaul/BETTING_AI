import re

def clean_name(name):
    """Limpia ruidos del OCR y sufijos de equipos."""
    # Quitar caracteres especiales
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
    
    # Sufijos comunes que ensucian la búsqueda estadística
    suffixes = [
        ' SE', ' FC', ' ES', ' UNPFM', ' United', ' U20', 
        ' CD', ' AS', ' AC', ' SA', ' Junior', ' Caldas'
    ]
    for s in suffixes:
        name = re.sub(rf'{s}$', '', name, flags=re.IGNORECASE)
    
    return name.strip()

def get_team_stats(home, away):
    """
    Consulta estadísticas basadas en nombres limpios.
    """
    home_clean = clean_name(home)
    away_clean = clean_name(away)
    
    # Simulación de respuesta funcional
    # Aquí puedes integrar tu API-Football o similar
    return {
        'home_goals_avg': 1.6, 
        'away_goals_avg': 1.1,
        'home_form': 0.8, # 80% efectividad
        'away_form': 0.4,
        'home_name': home_clean,
        'away_name': away_clean
    }
