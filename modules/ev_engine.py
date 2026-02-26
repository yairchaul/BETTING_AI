from modules.schemas import PickResult
from modules.team_analyzer import analyze_team_strength
from modules.google_context import get_google_context
from modules.odds_provider import get_market_odds
import math
import random


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def calculate_probability(stats, context, market):

    base = (
        stats["home_strength"] * 0.30 +
        stats["goal_expectancy"] / 4 * 0.25 +
        stats["attack_home"] * 0.20 +
        (0.5 + context) * 0.15 +
        random.uniform(-0.05, 0.05)
    )

    if market == "Home Win":
        base += 0.05

    elif market == "Away Win":
        base -= 0.03

    elif market == "Draw":
        base *= 0.75

    elif market == "Over 1.5":
        base += stats["goal_expectancy"] * 0.05

    elif market == "Over 2.5":
        base += stats["goal_expectancy"] * 0.02

    elif market == "Under 3.5":
        base -= stats["goal_expectancy"] * 0.03

    elif market == "BTTS Yes":
        base += (
            stats["attack_home"] +
            stats["attack_away"]
        ) * 0.05

    prob = sigmoid(base)

    # 🔥 Anti fake 0.95 probabilities
    prob = max(0.40, min(prob, 0.82))

    return prob


def analyze_matches(games):

    results = []

    for g in games:

        home = g["home"]
        away = g["away"]

        stats = analyze_team_strength(home, away)
        context = get_google_context(home, away)
        odds = get_market_odds(home, away)

        best_pick = None
        best_ev = -999

        # 🔥 MERCADOS COMPITEN ENTRE SÍ
        for market, odd in odds.items():

            prob = calculate_probability(stats, context, market)

            ev = (prob * odd) - 1

            # penalización confianza falsa
            ev -= random.uniform(0.02, 0.06)

            if ev > best_ev:
                best_ev = ev
                best_pick = PickResult(
                    match=f"{home} vs {away}",
                    selection=market,
                    probability=round(prob, 2),
                    odd=round(odd, 2),
                    ev=round(ev, 2)
                )

        if best_pick and best_pick.ev > 0:
            results.append(best_pick)

    return results


def build_parlay(games):
    return analyze_matches(games)

