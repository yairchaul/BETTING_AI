import random
from modules.caliente_api import get_market_lines


class EVEngine:

    def __init__(self):
        pass

    # =============================
    # MODELO IA (SIMULADO)
    # =============================
    def model_probability(self):
        return random.randint(55, 92)

    # =============================
    # ANALISIS INDIVIDUAL
    # =============================
    def cascade_analysis(self, local, visitante):

        markets = get_market_lines(local, visitante)
        prob = self.model_probability()

        if prob >= 85:
            return {
                "partido": f"{local} vs {visitante}",
                "pick": "Over 1.5 goles 1T",
                "probabilidad": prob,
                "cuota": 1.65
            }

        if prob >= 75:
            line = markets["totals"][1]
            return {
                "partido": f"{local} vs {visitante}",
                "pick": f"Over {line} goles",
                "probabilidad": prob,
                "cuota": 1.75
            }

        if prob >= 65:
            line = markets["corners"][0]
            return {
                "partido": f"{local} vs {visitante}",
                "pick": f"Over {line} corners",
                "probabilidad": prob,
                "cuota": 1.85
            }

        return {
            "partido": f"{local} vs {visitante}",
            "pick": f"Gana {local}",
            "probabilidad": prob,
            "cuota": 2.00
        }

    # =============================
    # CONSTRUCCION PARLAY
    # =============================
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

    # =============================
    # SIMULADOR DE GANANCIA
    # =============================
    def simulate_parlay_profit(self, parlay, monto):

        cuota_total = 1

        for pick in parlay:
            cuota_total *= pick["cuota"]

        ganancia = monto * cuota_total
        profit = ganancia - monto

        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(ganancia, 2),
            "ganancia_neta": round(profit, 2)
        }
