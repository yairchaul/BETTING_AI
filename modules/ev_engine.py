import math
from typing import Dict, List, Optional

# --- IMPORTACIÓN ROBUSTA DE TUS MÓDULOS ---
try:
    from modules.team_analyzer import build_team_profile
    from modules.schemas import PickResult, ParlayResult
except ModuleNotFoundError:
    # Esto ayuda si ejecutas desde diferentes niveles de carpeta
    try:
        from team_analyzer import build_team_profile
        from schemas import PickResult, ParlayResult
    except:
        # Failsafe para evitar el crash de importación
        pass

# Configuración Sharp
MIN_EV = 0.02
MIN_PROB = 0.25

def poisson_prob(lambda_: float, k: int) -> float:
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odd: float) -> float:
    if not odd or odd <= 0: return -1.0
    return (prob * odd) - 1

def calculate_caliente_probabilities(home_name: str, away_name: str):
    # Usamos tu analizador dinámico de últimos 5 partidos
    h_p = build_team_profile(home_name)
    a_p = build_team_profile(away_name)

    # Convertimos los scores de forma (0.0 a 1.0) y ataque en Lambdas de goles
    lh = (h_p.get("attack", 50) / a_p.get("defense", 50)) * 1.25 * (0.8 + h_p.get("form_score", 0.5) * 0.4)
    la = (a_p.get("attack", 50) / h_p.get("defense", 50)) * 1.10 * (0.8 + a_p.get("form_score", 0.5) * 0.4)
    
    p_win_h, p_draw, p_win_a = 0.0, 0.0, 0.0
    p_btts, p_o25 = 0.0, 0.0

    for i in range(7):
        for j in range(7):
            prob = poisson_prob(lh, i) * poisson_prob(la, j)
            if i > j: p_win_h += prob
            elif i == j: p_draw += prob
            else: p_win_a += prob
            
            if i > 0 and j > 0: p_btts += prob
            if (i + j) > 2.5: p_o25 += prob

    return {
        "Gana Local": p_win_h,
        "Empate": p_draw,
        "Gana Visitante": p_win_a,
        "Ambos Anotan": p_btts,
        "Over 2.5 Goles": p_o25
    }

def analyze_match(match: Dict) -> Optional[Dict]:
    h_name = match.get("home") or match.get("home_team")
    a_name = match.get("away") or match.get("away_team")
    
    if not h_name or not a_name: return None

    raw_odds = match.get("odds", {})
    # Buscamos cuotas en cualquier formato que traiga el OCR
    odds_map = {
        "Gana Local": raw_odds.get("Gana Local") or match.get("home_odd") or match.get("Local"),
        "Empate": raw_odds.get("Empate") or match.get("draw_odd") or match.get("Empate"),
        "Gana Visitante": raw_odds.get("Gana Visitante") or match.get("away_odd") or match.get("Visitante"),
        "Ambos Anotan": raw_odds.get("Ambos Anotan"),
        "Over 2.5 Goles": raw_odds.get("Over 2.5 Goles")
    }

    probs = calculate_caliente_probabilities(h_name, a_name)
    candidates = []
    reporte = []

    for market, prob in probs.items():
        odd = odds_map.get(market)
        if not odd or odd == 0: continue
        
        ev = calculate_ev(prob, float(odd))
        reporte.append(f"{market}: {int(prob*100)}% | EV: {round(ev, 2)}")
        
        if ev >= MIN_EV and prob >= MIN_PROB:
            candidates.append({"market": market, "prob": prob, "odd": float(odd), "ev": ev})

    if not candidates: return None
    best = max(candidates, key=lambda x: x["ev"])
    
    pick_obj = PickResult(
        match=f"{h_name} vs {a_name}",
        selection=best["market"],
        probability=round(best["prob"], 3),
        odd=best["odd"],
        ev=round(best["ev"], 3)
    )
    return {"pick": pick_obj, "text": "\n".join(reporte)}

def analyze_matches(matches: List[Dict]) -> List[Dict]:
    results = []
    for m in matches:
        res = analyze_match(m)
        if res: results.append(res)
    return results

def build_smart_parlay(picks: List[PickResult], max_picks=3) -> Optional[ParlayResult]:
    if not picks: return None
    selected = sorted(picks, key=lambda x: x.ev, reverse=True)[:max_picks]
    t_odd, t_prob = 1.0, 1.0
    for p in selected:
        t_odd *= p.odd
        t_prob *= p.probability
    return ParlayResult(
        matches=[p.match for p in selected],
        total_odd=round(t_odd, 2),
        combined_prob=round(t_prob, 3),
        total_ev=round(calculate_ev(t_prob, t_odd), 3)
    )
