import math


def poisson_prob(lmbda, k):
    return (lmbda**k * math.exp(-lmbda)) / math.factorial(k)


def score_matrix(lambda_home, lambda_away, max_goals=6):

    matrix = {}

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = poisson_prob(lambda_home, h) * poisson_prob(lambda_away, a)
            matrix[(h, a)] = p

    return matrix


def market_probabilities(lambda_home, lambda_away):

    matrix = score_matrix(lambda_home, lambda_away)

    home = 0
    draw = 0
    away = 0
    over15 = 0
    over25 = 0
    btts = 0

    for (h, a), p in matrix.items():

        if h > a:
            home += p
        elif h == a:
            draw += p
        else:
            away += p

        if h + a >= 2:
            over15 += p

        if h + a >= 3:
            over25 += p

        if h > 0 and a > 0:
            btts += p

    return {
        "HOME": home,
        "DRAW": draw,
        "AWAY": away,
        "OVER15": over15,
        "OVER25": over25,
        "BTTS": btts,
    }
