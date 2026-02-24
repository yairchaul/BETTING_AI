import random
from googleapiclient.discovery import build
from modules.schemas import MatchResult


class EVEngine:

    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id

        self.service = build(
            "customsearch",
            "v1",
            developerKey=self.api_key
        )

    def analyze_matches(self, teams_list):

        resultados = []
        parlay_sugerido = []

        # agrupar equipos
        for i in range(0, len(teams_list) - 1, 2):

            local = teams_list[i]
            visitante = teams_list[i + 1]

            prob = random.randint(45, 95)

            pick = (
                f"Gana {local}"
                if prob >= 70
                else "Doble Oportunidad / Empate"
            )

            match = MatchResult(
                partido=f"{local} vs {visitante}",
                pick=pick,
                probabilidad=prob
            )

            resultados.append(match)

            if prob >= 75:
                parlay_sugerido.append(match)

        return resultados, parlay_sugerido
