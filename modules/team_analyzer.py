import random

def analyze_team_strength(home, away):
    """
    Simulación dinámica estilo modelo estadístico.
    NO depende del nombre del equipo.
    """

    base_home = random.uniform(0.45, 0.75)
    base_away = random.uniform(0.35, 0.65)

    goal_expectancy = random.uniform(1.8, 3.4)

    attack_home = random.uniform(0.4, 0.8)
    attack_away = random.uniform(0.4, 0.8)

    defense_home = random.uniform(0.3, 0.7)
    defense_away = random.uniform(0.3, 0.7)

    return {
        "home_strength": base_home,
        "away_strength": base_away,
        "goal_expectancy": goal_expectancy,
        "attack_home": attack_home,
        "attack_away": attack_away,
        "defense_home": defense_home,
        "defense_away": defense_away
    }
