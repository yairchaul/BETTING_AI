import math
from typing import Dict, List, Optional
try:
    from modules.team_analyzer import build_team_profile
    from modules.schemas import PickResult, ParlayResult
except ImportError:
    from team_analyzer import build_team_profile
    from schemas import PickResult, ParlayResult

def poisson_prob(lambda_: float, k: int) -> float:
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odd: float) -> float:
    return (prob * odd) - 1

def analyze_match(match: Dict) -> Optional[Dict]:
    h_name = match.get("home") or match.get("home_team")
    a_name = match.get("away") or match.get("away_team")
    odds = match.get("odds", {})

    h_p = build_team_profile(h_name)
    a_p = build_team_profile(a_name)

    lh = (h_p["attack"] / a_p["defense"]) * 1.25 * (0.8 + h_p["form_score"] * 0.4)
    la = (a_p["attack"] / h_p["defense"]) * 1.10 * (0.8 + a_p["form_score"] * 0.4)
    
    # Mercados solicitados
    probs = {
        f"Gana {h_name}": 0.0, f"Gana {a_name}": 0.0, "Empate": 0.0,
        "Ambos Anotan": 0.0, "Over 2.5": 0.0, "Under 2.5": 0.0
    }

    for i in range(7):
        for j in range(7):
            p = poisson_prob(lh, i) * poisson_prob(la, j)
            if i > j: probs[f"Gana {h_name}"] += p
            elif i == j: probs["Empate"] += p
            else: probs[f"Gana {a_name}"] += p
            if i > 0 and j > 0: probs["Ambos Anotan"] += p
            if (i + j) > 2.5: probs["Over 2.5"] += p
            else: probs["Under 2.5"] += p

    candidates = []
    text_report = ""
    for m, prob in probs.items():
        odd = odds.get(m)
        if odd:
            ev = calculate_ev(prob, float(odd))
            text_report += f"{m}: {int(prob*100)}% | EV: {round(ev,2)}\n"
            if ev > 0.02:
                candidates.append(PickResult(f"{h_name} vs {a_name}", m, prob, float(odd), ev))

    if not candidates: return None
    best = max(candidates, key=lambda x: x.ev)
    return {"pick": best, "text": text_report}

def analyze_matches(matches: List[Dict]) -> List[Dict]:
    results = []
    for m in matches:
        res = analyze_match(m)
        if res: results.append(res)
    return results

def build_smart_parlay(picks: List[PickResult]) -> Optional[ParlayResult]:
    if not picks: return None
    selected = sorted(picks, key=lambda x: x.ev, reverse=True)[:5]
    t_odd, t_prob = 1.0, 1.0
    for p in selected:
        t_odd *= p.odd
        t_prob *= p.probability
    return ParlayResult([f"{p.match} ({p.selection})" for p in selected], round(t_odd, 2), round(t_prob, 3), round(calculate_ev(t_prob, t_odd), 2))
