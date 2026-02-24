import random
from modules.caliente_api import get_market_lines


class EVEngine:

    def __init__(self):
        pass

    def model_probability(self):
        """
        Simulación modelo IA.
        Luego conectaremos stats reales.
        """
        return random.randint(55, 92)

    def cascade_analysis(self, local, visitante):

        markets = get_market_lines(local, visitante)

        prob = self.model_probability()

        # =====================
        # NIVEL 1 — OVER 1T
        # =====================
        if prob >= 85:
            return {
                "partido": f"{local} vs {visitante}",
                "pick": "Over 1.5 goles 1T",
                "probabilidad": prob
            }

        # =====================
        # NIVEL 2 — OVER GOLES
        # =====================
        if prob >= 75:
            line = markets["totals"][1]
            return {
                "partido": f"{local} vs {visitante}",
                "pick": f"Over {line} goles",
                "probabilidad": prob
            }

        # =====================
        # NIVEL 3 — CORNERS
        # =====================
        if prob >= 65:
            line = markets["corners"][0]
            return {
                "partido": f"{local} vs {visitante}",
                "pick": f"Over {line} corners",
                "probabilidad": prob
            }

        # =====================
        # NIVEL 4 — GANADOR
        # =====================
        return {
            "partido": f"{local} vs {visitante}",
            "pick": f"Gana {local}",
            "probabilidad": prob
        }

    def build_parlay(self, equipos):

        resultados = []
        parlay = []

        for i in range(0, len(equipos) - 1, 2):

            local = equipos[i]
            visitante = equipos[i + 1]

            analisis = self.cascade_analysis(local, visitante)

            resultados.append(analisis)

            if analisis["probabilidad"] >= 80:
                parlay.append(analisis)

        return resultados, parlay
