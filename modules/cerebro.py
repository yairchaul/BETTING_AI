from modules.schemas import Pick
from modules.learning import success_rate


class StrategyEngine:

    def decide(self, match, probs):

        rate = success_rate()

        boost = 0.05 if rate > 60 else -0.05

        over = probs["over15"] + boost
        btts = probs["btts"] + boost

        if over > 0.80:
            return Pick(
                partido=f"{match.home} vs {match.away}",
                pick="Over 1.5 goles",
                probabilidad=int(over*100),
                cuota=1.60
            )

        if btts > 0.70:
            return Pick(
                partido=f"{match.home} vs {match.away}",
                pick="Ambos anotan",
                probabilidad=int(btts*100),
                cuota=1.75
            )

        return Pick(
            partido=f"{match.home} vs {match.away}",
            pick=f"Gana {match.home}",
            probabilidad=65,
            cuota=1.85
        )
