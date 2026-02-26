import math

def clamp(x):
    return max(0.05, min(0.95, x))


def poisson_prob(l, k):
    if l <= 0:
        return 1 if k == 0 else 0
    return (math.exp(-l)*(l**k))/math.factorial(k)


def calculate_match_probabilities(home, away, context=None):

    h_form = home["form_score"]
    a_form = away["form_score"]

    lh = (home["attack"]/away["defense"]) * 1.25 * (0.8+h_form*0.4)
    la = (away["attack"]/home["defense"]) * 0.85 * (0.8+a_form*0.4)

    p_home=p_draw=p_away=0
    p_btts=p_o25=p_o35=0
    p_h_o15=p_h_o25=p_a_o15=p_a_o25=0

    for i in range(7):
        for j in range(7):

            prob = poisson_prob(lh,i)*poisson_prob(la,j)
            tg=i+j

            if i>j: p_home+=prob
            elif i==j: p_draw+=prob
            else: p_away+=prob

            if i>0 and j>0:
                p_btts+=prob

            if tg>2.5: p_o25+=prob
            if tg>3.5: p_o35+=prob

            if i>j and tg>1.5: p_h_o15+=prob
            if i>j and tg>2.5: p_h_o25+=prob
            if j>i and tg>1.5: p_a_o15+=prob
            if j>i and tg>2.5: p_a_o25+=prob

    return {
        "Resultado Final (Local)":clamp(p_home),
        "Resultado Final (Empate)":clamp(p_draw),
        "Resultado Final (Visita)":clamp(p_away),
        "Doble Oportunidad (L/E)":clamp(p_home+p_draw),
        "Doble Oportunidad (V/E)":clamp(p_away+p_draw),
        "Ambos Anotan":clamp(p_btts),
        "Over 2.5 Goles":clamp(p_o25),
        "Under 2.5 Goles":clamp(1-p_o25),
        "Over 3.5 Goles":clamp(p_o35),
        "Local y Over 1.5":clamp(p_h_o15),
        "Local y Over 2.5":clamp(p_h_o25),
        "Visita y Over 1.5":clamp(p_a_o15),
        "Visita y Over 2.5":clamp(p_a_o25),
    }
