import math

# =====================================
# UTILIDADES
# =====================================

def poisson_prob(lmbda, k):

    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)


def clamp(x):
    return max(0.05, min(0.90, x))


# =====================================
# MATCH PROBABILITY ENGINE
# =====================================

def calculate_match_probabilities(home_p, away_p):

    """
    Devuelve probabilidades BASE estables.
    ESTE FORMATO ES INAMOVIBLE.
    """

    attack_home = home_p.get("attack", 1.3)
    defense_home = home_p.get("defense", 1.2)

    attack_away = away_p.get("attack", 1.2)
    defense_away = away_p.get("defense", 1.3)

    # Expected goals
    lambda_home = attack_home / defense_away * 1.25
    lambda_away = attack_away / defense_home * 1.05

    p_home = 0
    p_draw = 0
    p_away = 0

    # Matriz Poisson 6x6
    for i in range(6):
        for j in range(6):

            prob = poisson_prob(lambda_home, i) * poisson_prob(lambda_away, j)

            if i > j:
                p_home += prob
            elif i == j:
                p_draw += prob
            else:
                p_away += prob

    total = p_home + p_draw + p_away

    return {
        "home": clamp(p_home / total),
        "draw": clamp(p_draw / total),
        "away": clamp(p_away / total),
    }
