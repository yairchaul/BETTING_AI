from modules.schemas import Match
from modules.stats_fetch import fetch_team_stats
from modules.cerebro import StrategyEngine


class EVEngine:

    def __init__(self):
        self.brain = StrategyEngine()

    def build_parlay(self, equipos):

        resultados = []
        parlay = []

        for i in range(0, len(equipos)-1,2):

            match = Match(equipos[i], equipos[i+1])

            probs = fetch_team_stats(match.home, match.away)

            pick = self.brain.decide(match, probs)

            resultados.append(pick)

            if pick.probabilidad >= 75:
                parlay.append(pick)

        return resultados, parlay


