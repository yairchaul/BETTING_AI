import random
from modules.caliente_api import get_events, extract_match_odds


class EVEngine:

    def __init__(self):
        self.events = get_events()

    def probability_model(self):
        return random.randint(55, 90)

    def cascade_pick(self, local, visitante):

        odds = extract_match_odds(
            self.events,
            local,
            visitante
        )

        if not odds:
            return "Sin mercado disponible", 50

        prob = self.probability_model()

        # NIVEL 1 — Over 1.5 HT
        if prob > 80:
            return "Over 1.5 goles 1T", prob

        # NIVEL 2 — Over Total Goals
        if prob > 70 and odds["totals"]:
            line = odds["totals"][0]["line"]
            return f"Over {line} goles", prob

        # NIVEL 3 — Corners
        if prob > 65 and odds["corners"]:
            line = odds["corners"][0]["line"]
            return f"Over {line} corners", prob

        # NIVEL 4 — Winner
        if odds["winner"]:
            return f"Gana {local}", prob

        return "No bet", 50
