import random


def get_match_context(home, away):
    """
    Contexto externo tipo noticias / momentum.
    """

    return {
        "injuries": random.choice([0, 1]),
        "importance": random.uniform(0.4, 1.0),
        "public_hype": random.uniform(0.3, 1.0),
    }
