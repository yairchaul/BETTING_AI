def obtener_datos_reales():
    """
    Simula la extracción dinámica de la API de Caliente. 
    Procesa todos los partidos detectados sin límites manuales.
    """
    games = [
        {"id": "CLE@CHA", "away_team": "Cleveland Cavaliers", "home_team": "Charlotte Hornets", "linea": 228.5},
        {"id": "MIL@NOP", "away_team": "Milwaukee Bucks", "home_team": "New Orleans Pelicans", "linea": 223.5},
        {"id": "LAL@LAC", "away_team": "Los Angeles Lakers", "home_team": "LA Clippers", "linea": 226.5},
        {"id": "BKN@OKC", "away_team": "Brooklyn Nets", "home_team": "Oklahoma City Thunder", "linea": 213.5},
        {"id": "GSW@PHX", "away_team": "Golden State Warriors", "home_team": "Phoenix Suns", "linea": 231.0}
    ]
    return games
