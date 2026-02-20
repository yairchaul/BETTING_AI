def obtener_datos_reales():
    """
    Simula la extracción de todos los partidos de la API de Caliente.
    En un entorno real, aquí iría el request.get() a la API.
    """
    # Lista dinámica de todos los partidos detectados hoy
    games = [
        {"id": "CLE@CHA", "game": "Cleveland Cavaliers vs Charlotte Hornets", "linea": 228.5},
        {"id": "MIL@NOP", "game": "Milwaukee Bucks vs New Orleans Pelicans", "linea": 223.5},
        {"id": "LAL@LAC", "game": "Los Angeles Lakers vs LA Clippers", "linea": 226.5},
        {"id": "BKN@OKC", "game": "Brooklyn Nets vs Oklahoma City Thunder", "linea": 213.5},
        {"id": "GSW@PHX", "game": "Golden State Warriors vs Phoenix Suns", "linea": 231.0}
    ]
    return games
