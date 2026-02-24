import random
from modules.schemas import MatchResult


class EVEngine:

    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id

    # -------------------------
    # SIMULADORES PROBABILIDAD
    # (Luego se conectan APIs reales)
    # -------------------------

    def prob_first_half_over(self):
        return random.randint(30, 85)

    def prob_total_goals(self):
        return random.randint(40, 90)

    def prob_corners(self):
        return random.randint(35, 80)

    def prob_winner(self):
        return random.randint(45, 95)

    # -------------------------
    # CASCADE LOGIC
    # -------------------------

    def cascade_analysis(self, local, visitante):

        # 1️⃣ Over 1.5 HT
        p1 = self.prob_first_half_over()
        if p1 >= 75:
            return "Over 1.5 goles 1T", p1

        # 2️⃣ Over Total
        p2 = self.prob_total_goals()
        if p2 >= 70:
            return "Over goles totales", p2

        # 3️⃣ Corners
        p3 = self.prob_corners()
        if p3 >= 70:
            return "Over tiros de esquina", p3

        # 4️⃣ Ganador
        p4 = self.prob_winner()
        if p4 >= 65:
            return f"Gana {local}", p4

        # 5️⃣ Combo premium
        p5 = random.randint(60, 95)
        return f"{local} gana + Over goles", p5

    # -------------------------
    # ANALISIS GENERAL
    # -------------------------

    def analyze_matches(self, equipos):

        resultados = []
        parlay = []

        for i in range(0, len(equipos) - 1, 2):

            local = equipos[i]
            visitante = equipos[i + 1]

            pick, prob = self.cascade_analysis(local, visitante)

            match = MatchResult(
                partido=f"{local} vs {visitante}",
                pick=pick,
                probabilidad=prob
            )

            resultados.append(match)

            if prob >= 75:
                parlay.append(match)

        return resultados, parlay
