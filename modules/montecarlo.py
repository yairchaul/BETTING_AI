import math


# ======================
# POISSON
# ======================

def poisson(lmbda, k):
    return (lmbda ** k * math.exp(-lmbda)) / math.factorial(k)


# ======================
# MATRIZ DE MARCADORES
# ======================

def score_matrix(lambda_home, lambda_away, max_goals=6):

    matrix = {}

    for h in range(max_goals):
        for a in range(max_goals):

            prob = poisson(lambda_home, h) * poisson(lambda_away, a)
            matrix[(h, a)] = prob

    return matrix


# ======================
# PROBABILIDADES MERCADO
# ======================

def market_probabilities(lambda_home, lambda_away):

    matrix = score_matrix(lambda_home, lambda_away)

    p_home = 0
    p_draw = 0
    p_away = 0

    over15 = 0
    over25 = 0
    over35 = 0
    btts = 0

    for (h, a), p in matrix.items():

        # RESULTADO
        if h > a:
            p_home += p
        elif h == a:
            p_draw += p
        else:
            p_away += p

        total_goals = h + a

        # GOLES
        if total_goals >= 2:
            over15 += p

        if total_goals >= 3:
            over25 += p

        if total_goals >= 4:
            over35 += p

        # BTTS
        if h > 0 and a > 0:
            btts += p

    return {
        "HOME": p_home,
        "DRAW": p_draw,
        "AWAY": p_away,
        "OVER15": over15,
        "OVER25": over25,
        "OVER35": over35,
        "BTTS": btts,
    }

