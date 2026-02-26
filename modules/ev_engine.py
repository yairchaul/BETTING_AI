# modules/ev_engine.py
# ev_engine.py  --  versión mejorada 2025/26 – más mercados, menos empate automático

import random
from typing import Dict, List, Optional
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context

# ────────────────────────────────────────────────
# UTILIDADES
# ────────────────────────────────────────────────
def clamp(x: float) -> float:
    return max(0.01, min(0.99, x))


def expected_value(prob: float, odd: float) -> float:
    return (prob * odd) - 1


def poisson_prob(lambda_: float, k: int) -> float:
    """Probabilidad Poisson simplificada (k = 0,1,2,3+)"""
    if k == 0:
        return pow(2.71828, -lambda_)
    elif k == 1:
        return lambda_ * pow(2.71828, -lambda_)
    elif k == 2:
        return (lambda_ ** 2 / 2) * pow(2.71828, -lambda_)
    else:  # 3 o más
        return 1 - (poisson_prob(lambda_, 0) + poisson_prob(lambda_, 1) + poisson_prob(lambda_, 2))


# ────────────────────────────────────────────────
# CÁLCULO DE LAMBDA (goles esperados)
# ────────────────────────────────────────────────
def calculate_lambdas(home: Dict, away: Dict, context: Dict) -> tuple[float, float]:
    # Goles esperados base
    home_attack  = home.get("attack",  home.get("attack_home",  1.35))
    away_defense = away.get("defense", away.get("defense_away", 1.30))
    away_attack  = away.get("attack",  away.get("attack_away",  1.10))
    home_defense = home.get("defense", home.get("defense_home", 1.25))

    # Ajustes
    home_adv     = 0.28                      # ventaja local típica
    tempo        = (home.get("tempo", 0.5) + away.get("tempo", 0.5)) / 2
    tempo_factor = 0.7 + tempo * 0.6         # 0.7–1.3

    lambda_home = (home_attack / away_defense) * home_adv * tempo_factor
    lambda_away = (away_attack / home_defense) * (1.0 / home_adv) * tempo_factor

    # Contexto (lesiones, motivación, etc.)
    lambda_home *= (1 + context.get("home_boost", 0.0))
    lambda_away *= (1 + context.get("away_boost", 0.0))
    lambda_home *= (1 - context.get("injuries_home", 0.0) * 0.15)
    lambda_away *= (1 - context.get("injuries_away", 0.0) * 0.15)

    return round(lambda_home, 2), round(lambda_away, 2)


# ────────────────────────────────────────────────
# TODOS LOS MERCADOS – probabilidades independientes
# ────────────────────────────────────────────────
def calculate_all_market_probs(
    home_profile: Dict,
    away_profile: Dict,
    context: Dict
) -> Dict[str, float]:

    λh, λa = calculate_lambdas(home_profile, away_profile, context)

    # 1×2
    home_win   = 0.0
    draw       = 0.0
    away_win   = 0.0
    for i in range(10):
        for j in range(10):
            p = poisson_prob(λh, i) * poisson_prob(λa, j)
            if i > j:   home_win += p
            elif i == j: draw    += p
            else:       away_win += p

    # Over / Under
    total_goals_exp = λh + λa
    over_2_5   = 1 - (poisson_prob(total_goals_exp, 0) +
                      poisson_prob(total_goals_exp, 1) +
                      poisson_prob(total_goals_exp, 2))
    under_2_5  = 1 - over_2_5
    over_1_5   = 1 - (poisson_prob(total_goals_exp, 0) + poisson_prob(total_goals_exp, 1))

    # BTTS
    btts_yes = 1 - (poisson_prob(λh, 0) + poisson_prob(λa, 0) - poisson_prob(λh, 0) * poisson_prob(λa, 0))
    btts_no  = 1 - btts_yes

    # Corners (estimación muy simplificada)
    corners_exp = 9.0 + (total_goals_exp - 2.5) * 1.4
    corners_over_8_5 = 0.45 + (corners_exp - 9.0) * 0.09
    corners_over_8_5 = clamp(corners_over_8_5)

    probs = {
        "Gana Local"     : clamp(home_win   + 0.03),   # pequeño boost local
        "Empate"         : clamp(draw),
        "Gana Visitante" : clamp(away_win),
        "Over 2.5"       : clamp(over_2_5   + 0.02 * (total_goals_exp > 2.8)),
        "Under 2.5"      : clamp(under_2_5),
        "BTTS Sí"        : clamp(btts_yes),
        "BTTS No"        : clamp(btts_no),
        "Over 1.5"       : clamp(over_1_5),
        "Corners Over 8.5": clamp(corners_over_8_5),
    }

    return probs


# ────────────────────────────────────────────────
# ANÁLISIS DE UN PARTIDO – genera reporte como pediste
# ────────────────────────────────────────────────
def analyze_match(match: Dict) -> Optional[Dict]:

    home_profile = build_team_profile(match["home"])
    away_profile = build_team_profile(match["away"])
    context      = get_match_context(match["home"], match["away"])

    probs = calculate_all_market_probs(home_profile, away_profile, context)

    # ── Formato exacto que pediste ──────────────────────────────────────
    lines = []
    lines.append(f"Empate              {int(probs['Empate']*100)}%")
    lines.append(f"BTTS Sí             {int(probs['BTTS Sí']*100)}%")
    lines.append(f"Over 2.5            {int(probs['Over 2.5']*100)}%")
    lines.append(f"Local Win           {int(probs['Gana Local']*100)}%")
    lines.append(f"Under 2.5           {int(probs['Under 2.5']*100)}%")
    lines.append(f"Corners Over 8.5    {int(probs['Corners Over 8.5']*100)}%")

    # Pick recomendado = el de mayor probabilidad
    best_market = max(probs.items(), key=lambda x: x[1])
    best_name   = best_market[0]
    best_prob   = int(best_market[1] * 100)

    lines.append("")
    lines.append(f"Resultado esperado después del análisis en el partido")
    lines.append(f"{match['home']} vs {match['away']}: corresponde al **{best_name}** ({best_prob}%)")

    analysis_text = "\n".join(lines)

    # Para mantener compatibilidad con tu sistema anterior
    pick = PickResult(
        match     = f"{match['home']} vs {match['away']}",
        selection = best_name,
        probability = round(best_market[1], 3),
        odd       = 1.0,                # placeholder – puedes mapear odds reales después
        ev        = 0.0
    )

    return {
        "text": analysis_text,
        "pick": pick,
        "all_probs": probs,
        "lambdas": calculate_lambdas(home_profile, away_profile, context)
    }


# ────────────────────────────────────────────────
# MÚLTIPLES PARTIDOS
# ────────────────────────────────────────────────
def analyze_matches(matches: List[Dict]) -> List[Dict]:
    results = []
    for match in matches:
        result = analyze_match(match)
        if result:
            results.append(result)
    return results


# Ejemplo de uso (para pruebas)
if __name__ == "__main__":
    ejemplo = {
        "home": "América",
        "away": "Cruz Azul"
    }
    res = analyze_match(ejemplo)
    if res:
        print(res["text"])
