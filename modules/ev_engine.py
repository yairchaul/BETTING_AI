import math
from typing import Dict, List, Optional
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context

# ======================================
# CONFIGURACIÓN SHARP (FILTROS FINALES)
# ======================================
MIN_EV = 0.05    # 5% de ventaja mínima sobre la casa
MIN_PROB = 0.30  # Probabilidad mínima para considerar un mercado

# ======================================
# UTILIDADES MATEMÁTICAS
# ======================================
def poisson_prob(lambda_: float, k: int) -> float:
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odd: float) -> float:
    return (prob * odd) - 1

# ======================================
# MOTOR DE PROBABILIDADES CALIENTE.MX
# ======================================
def calculate_caliente_probabilities(home_p: Dict, away_p: Dict, context: Dict) -> Dict[str, float]:
    """
    Calcula probabilidades basadas en los últimos 5 partidos (vía team_profile)
    y las mapea a los mercados reales de Caliente.mx.
    """
    # 1. Ajuste por forma reciente (Tendencia de los últimos 5 partidos)
    h_form = home_p.get("form_score", 0.5) 
    a_form = away_p.get("form_score", 0.5)

    # 2. Goles Esperados (Lambdas) ajustados
    lh = (home_p.get("attack", 1.2) / away_p.get("defense", 1.2)) * 1.25 * (0.8 + h_form * 0.4)
    la = (away_p.get("attack", 1.0) / home_p.get("defense", 1.2)) * 0.85 * (0.8 + a_form * 0.4)
    
    # 3. Matriz de Poisson para Mercados Reales
    p_win_h, p_draw, p_win_a = 0.0, 0.0, 0.0
    p_btts, p_o15, p_o25, p_o35 = 0.0, 0.0, 0.0, 0.0
    p_h_o15, p_h_o25, p_a_o15, p_a_o25 = 0.0, 0.0, 0.0, 0.0

    for i in range(7):
        for j in range(7):
            prob = poisson_prob(lh, i) * poisson_prob(la, j)
            total_g = i + j
            
            if i > j: p_win_h += prob
            elif i == j: p_draw += prob
            else: p_win_a += prob
            
            if i > 0 and j > 0: p_btts += prob
            if total_g > 1.5: p_o15 += prob
            if total_g > 2.5: p_o25 += prob
            if total_g > 3.5: p_o35 += prob

            # Resultado + Over (Mercados Caliente)
            if i > j and total_g > 1.5: p_h_o15 += prob
            if i > j and total_g > 2.5: p_h_o25 += prob
            if j > i and total_g > 1.5: p_a_o15 += prob
            if j > i and total_g > 2.5: p_a_o25 += prob

    return {
        "Resultado Final (Local)": p_win_h,
        "Resultado Final (Empate)": p_draw,
        "Resultado Final (Visita)": p_win_a,
        "Doble Oportunidad (L/E)": p_win_h + p_draw,
        "Doble Oportunidad (V/E)": p_win_a + p_draw,
        "Ambos Anotan": p_btts,
        "Over 2.5 Goles": p_o25,
        "Under 2.5 Goles": 1 - p_o25,
        "Resultado/Total Goles (L y O1.5)": p_h_o15,
        "Resultado/Total Goles (L y O2.5)": p_h_o25,
        "Resultado/Total Goles (V y O1.5)": p_a_o15,
        "Resultado/Total Goles (V y O2.5)": p_a_o25
    }

# ======================================
# ANÁLISIS POR PARTIDO (EL MEJOR EV)
# ======================================
def analyze_match(match: Dict) -> Optional[PickResult]:
    home, away = match.get("home"), match.get("away")
    odds = match.get("odds", {})
    if not odds: return None

    # Obtener perfiles (análisis últimos 5 partidos) y contexto
    h_profile = build_team_profile(home)
    a_profile = build_team_profile(away)
    context = get_match_context(home, away)

    # Calcular probabilidades reales
    probabilities = calculate_caliente_probabilities(h_profile, a_profile, context)

    candidates = []
    for market, prob in probabilities.items():
        if market not in odds: continue

        ev = calculate_ev(prob, odds[market])

        # Filtro de seguridad Sharp
        if ev >= MIN_EV and prob >= MIN_PROB:
            candidates.append(
                PickResult(
                    match=f"{home} vs {away}",
                    selection=market,
                    probability=round(prob, 3),
                    odd=odds[market],
                    ev=round(ev, 3)
                )
            )

    # Retornar SOLO el mercado con mejor EV por partido
    return max(candidates, key=lambda x: x.ev) if candidates else None

# ======================================
# PROCESAMIENTO GLOBAL
# ======================================
def analyze_matches(matches: List[Dict]) -> List[PickResult]:
    results = []
    for match in matches:
        res = analyze_match(match)
        if res: results.append(res)
    return results

# ======================================
# CONSTRUCTOR DE PARLAY INTELIGENTE
# ======================================
def build_smart_parlay(picks: List[PickResult], max_picks=4) -> Optional[ParlayResult]:
    if not picks: return None

    # Ordenar por EV para seleccionar las mejores oportunidades
    best_picks = sorted(picks, key=lambda x: x.ev, reverse=True)[:max_picks]

    t_odds, t_prob = 1.0, 1.0
    for p in best_picks:
        t_odds *= p.odd
        t_prob *= p.probability

    return ParlayResult(
        matches=[f"{p.match} ({p.selection})" for p in best_picks],
        total_odd=round(t_odds, 2),
        combined_prob=round(t_prob, 3),
        total_ev=round(calculate_ev(t_prob, t_odds), 3)
    )
