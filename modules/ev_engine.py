import numpy as np
import math
from scipy.stats import poisson

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def _parse_odd(self, o):
        """Convierte momio americano o basura de texto a decimal."""
        try:
            val = str(o).replace('+', '').strip()
            n = float(val)
            if n == 0: return 2.0
            return (n/100 + 1) if n > 0 else (100/abs(n) + 1)
        except:
            return 2.0

    def get_raw_probabilities(self, game):
        """Modelo de Cascada con Filtro de Élite (85%+)"""
        try:
            # 1. Preparación de cuotas
            ch = self._parse_odd(game.get('home_odd', 100))
            cv = self._parse_odd(game.get('away_odd', 100))
            ce = self._parse_odd(game.get('draw_odd', 100))

            # 2. Inferencia Real de Lambdas (Potencia de Goles)
            # Ajuste dinámico: a menor cuota, mayor lambda esperado
            lh = round(2.7 / (ch**0.7), 2)
            lv = round(2.7 / (cv**0.7), 2)

            # 3. Matriz de Probabilidad (Grid 10x10 para precisión)
            grid = 10
            dist_h = poisson.pmf(np.arange(grid), lh)
            dist_v = poisson.pmf(np.arange(grid), lv)
            m = np.outer(dist_h, dist_v)
            idx = np.indices(m.shape)
            total_goles = idx[0] + idx[1]

            # 4. Evaluación de la Cascada (Orden de Valor)
            opciones = [
                # Nivel 1: Combos de Alto Valor
                {"name": f"{game['home']} & Over 1.5", "p": np.sum(m * (idx[0] > idx[1]) * (total_goles > 1.5)), "c": round(ch * 1.32, 2)},
                {"name": f"{game['home']} & Over 2.5", "p": np.sum(m * (idx[0] > idx[1]) * (total_goles > 2.5)), "c": round(ch * 1.82, 2)},
                {"name": f"{game['away']} & Over 1.5", "p": np.sum(m * (idx[1] > idx[0]) * (total_goles > 1.5)), "c": round(cv * 1.32, 2)},
                {"name": f"{game['away']} & Over 2.5", "p": np.sum(m * (idx[1] > idx[0]) * (total_goles > 2.5)), "c": round(cv * 1.82, 2)},
                # Nivel 2: Mercados de Probabilidad
                {"name": "Ambos Anotan (BTTS)", "p": np.sum(m[1:, 1:]), "c": 1.90},
                {"name": "Over 2.5 Goles", "p": np.sum(m[total_goles > 2.5]), "c": 2.00},
                {"name": "Over 1.5 Goles", "p": np.sum(m[total_goles > 1.5]), "c": 1.35},
                # Nivel 3: Ganador Simple (1X2)
                {"name": f"Gana {game['home']}", "p": np.sum(m * (idx[0] > idx[1])), "c": ch},
                {"name": f"Gana {game['away']}", "p": np.sum(m * (idx[1] > idx[0])), "c": cv}
            ]

            # 5. Filtro de Seguridad (Threshold)
            validas = [o for o in opciones if o['p'] >= self.threshold]

            if not validas:
                return {"status": "DESCARTADO", "home": game['home'], "away": game['away'], "prob_max": round(max(o['p'] for o in opciones)*100, 1)}

            # 6. Selección del Mejor Momio entre los seguros
            mejor = max(validas, key=lambda x: x['c'])

            return {
                "status": "APROBADO",
                "home": game['home'],
                "away": game['away'],
                "pick": mejor['name'],
                "prob": round(mejor['p'] * 100, 1),
                "cuota": mejor['c'],
                "ev": round((mejor['p'] * mejor['c']) - 1, 3),
                "lh": lh, "lv": lv, "exp": round(lh + lv, 2)
            }

        except Exception as e:
            return {"status": "ERROR", "msg": str(e)}

    def simulate_parlay_profit(self, picks_aprobados, monto):
        """Calcula el rendimiento de un parlay con los picks que pasaron el filtro."""
        if not picks_aprobados:
            return {"cuota_total": 0, "pago_total": 0, "ganancia_neta": 0}

        cuota_total = 1.0
        for p in picks_aprobados:
            cuota_total *= p.get('cuota', 1.0)
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago, 2),
            "ganancia_neta": round(pago - monto, 2)
        }

