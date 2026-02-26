import re

def clean_name(name):
    """Limpia ruidos del OCR y sufijos de equipos."""
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
    suffixes = [' SE', ' FC', ' ES', ' UNPFM', ' United', ' U20', ' CD', ' Junior']
    for s in suffixes:
        name = re.sub(rf'{s}$', '', name, flags=re.IGNORECASE)
    return name.strip()

def build_team_rating(last5):
    """Convierte historial de partidos en ratings de ataque y defensa."""
    if not last5:
        return {"attack": 50, "defense": 50}

    goals_for = sum(m["gf"] for m in last5) / len(last5)
    goals_against = sum(m["ga"] for m in last5) / len(last5)
    shots_on_target = sum(m["shots"] for m in last5) / len(last5)

    # Lógica de cálculo
    attack = (goals_for * 35) + (shots_on_target * 5)
    defense = 100 - (goals_against * 30)

    # Limitar rango para evitar valores extremos que rompan la simulación
    attack = max(30, min(80, attack))
    defense = max(30, min(80, defense))

    return {
        "attack": attack,
        "defense": defense
    }

def get_team_stats(home, away):
    """
    Función principal llamada por el Cerebro.
    """
    home_clean = clean_name(home)
    away_clean = clean_name(away)

    # SIMULACIÓN DE DATOS (Aquí conectarás tu API en el futuro)
    # Simulamos un historial para el Local (3 goles a favor, 1 en contra, 5 tiros)
    mock_last5_home = [{"gf": 2, "ga": 1, "shots": 4}, {"gf": 3, "ga": 0, "shots": 6}]
    # Simulamos un historial para el Visitante
    mock_last5_away = [{"gf": 1, "ga": 2, "shots": 3}, {"gf": 0, "ga": 1, "shots": 2}]

    return {
        "home": build_team_rating(mock_last5_home),
        "away": build_team_rating(mock_last5_away)
    }
