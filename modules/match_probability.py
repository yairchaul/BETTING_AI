from modules.form_analyzer import analyze_last5
from modules.team_analyzer import build_team_profile
import math

def poisson_prob(l, k):
    return (math.exp(-l) * (l**k)) / math.factorial(k)

def calculate_match_probabilities(home, away):

    home_form = analyze_last5(home["matches"])
    away_form = analyze_last5(away["matches"])

    lh = (home_form["attack"] / away_form["defense"]) * 1.25
    la = (away_form["attack"] / home_form["defense"]) * 0.85

    p_win_h = p_draw = p_win_a = 0
    p_btts = p_o25 = 0

    for i in range(6):
        for j in range(6):
            p = poisson_prob(lh,i)*poisson_prob(la,j)

            if i>j: p_win_h+=p
            elif i==j: p_draw+=p
            else: p_win_a+=p

            if i>0 and j>0:
                p_btts+=p

            if i+j>2:
                p_o25+=p

    return {
        "Resultado Final (Local)": p_win_h,
        "Resultado Final (Empate)": p_draw,
        "Resultado Final (Visita)": p_win_a,
        "Ambos Anotan": p_btts,
        "Over 2.5 Goles": p_o25
    }
