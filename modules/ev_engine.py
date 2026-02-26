from typing import Dict, Optional
from modules.schemas import PickResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context
from modules.match_probability import calculate_match_probabilities

MIN_EV = 0.08
MIN_PROB = 0.35


def calculate_ev(prob, odds):
    return (prob * odds) - 1


def analyze_match(match: Dict) -> Optional[Dict]:

    h_name = match.get("home")
    a_name = match.get("away")

    home_p = build_team_profile(h_name)
    away_p = build_team_profile(a_name)

    context = get_match_context(h_name,a_name)

    probs = calculate_match_probabilities(
        home_p,
        away_p,
        context
    )

    odds = match.get("odds",{})

    market_results=[]

    for market,prob in probs.items():

        if market not in odds:
            continue

        ev = calculate_ev(prob,odds[market])

        if ev < MIN_EV or prob < MIN_PROB:
            continue

        market_results.append({
            "market":market,
            "prob":prob,
            "odds":odds[market],
            "ev":ev
        })

    if not market_results:
        return None

    best = max(market_results,key=lambda x:x["ev"])

    pick = PickResult(
        match=f"{h_name} vs {a_name}",
        selection=best["market"],
        probability=round(best["prob"],3),
        odd=best["odds"],
        ev=round(best["ev"],3)
    )

    text=f"""
⚽ {h_name} vs {a_name}
🎯 {best['market']}
📊 Prob: {best['prob']:.2%}
💰 Odd: {best['odds']}
📈 EV: {best['ev']:.2f}
"""

    return {
        "text":text,
        "pick":pick
    }
