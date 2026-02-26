def clean_name(name):
    """
    Elimina ruidos del OCR y sufijos innecesarios para la búsqueda estadística.
    """
    # Limpieza de caracteres especiales que a veces el OCR confunde
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
    
    suffixes = [
        ' SE', ' FC', ' ES', ' UNPFM', ' United', ' U20', 
        ' CD', ' AS', ' AC', ' SA', ' Junior'
    ]
    for s in suffixes:
        # Usamos regex para asegurar que solo borre el sufijo al final de la palabra
        name = re.sub(rf'{s}$', '', name, flags=re.IGNORECASE)
    
    return name.strip()

def get_team_stats(home, away):
    home_clean = clean_name(home)
    away_clean = clean_name(away)
    
    # Log de diagnóstico para el desarrollador (ver en consola)
    print(f"Buscando estadísticas para: {home_clean} vs {away_clean}")
    
    # Simulación de respuesta basada en nombres reales
    # Aquí es donde conectarás tu API de promedios de los últimos 5 partidos
    return {
        'home_goals_avg': 1.8 if "America" in home_clean else 1.2, 
        'away_goals_avg': 0.9 if "Tigres" in away_clean else 1.1,
        'home_form': 0.75,
        'away_form': 0.50
    }
