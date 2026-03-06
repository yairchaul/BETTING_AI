# modules/parlayimport numpy as np
import numpy as np


def build_parlay(picks):

    probs = [p["prob"] for p in picks]

    odds = [p["odds"] for p in picks]

    parlay_prob = np.prod(probs)

    parlay_odds = np.prod(odds)

    ev = (parlay_prob * parlay_odds) - 1

    return {
        "probability": parlay_prob,
        "odds": parlay_odds,
        "expected_value": ev
    }