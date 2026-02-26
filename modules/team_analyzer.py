import random


# =====================================
# TEAM PROFILE BUILDER
# =====================================

def build_team_profile(team_name: str):

    """
    Simula perfil estadístico del equipo.
    Luego podremos conectar APIs reales.
    """

    profile = {
        "team": team_name,
        "attack_rating": random.uniform(0.4, 0.9),
        "defense_rating": random.uniform(0.4, 0.9),
        "form": random.uniform(0.3, 1.0),
        "tempo": random.uniform(0.3, 1.0),
    }

    return profile
