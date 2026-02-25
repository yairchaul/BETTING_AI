import math
import numpy as np

class EVEngine:
    def poisson_pmf(self, k, lam):
        if lam <= 0: return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)

    def get_raw_probabilities(self, game):
        """Calcula probabilidades puras sin filtros de noticias."""
        h_odd = float(str(game['home_odd']).replace('+', '').strip())
        h_dec = (h_odd/100 + 1) if h_odd > 0 else (100/abs(h_odd) + 1)
        prob_implied = 1 / h_dec

        # Lambdas base
        l_home = 2.4 * prob_implied
        l_away = 1.3 * (1 - prob_implied)

        matrix = np.zeros((6, 6))
        for h in range(6):
            for a in range(6):
                matrix[h, a] = self.poisson_pmf(h, l_home) * self.poisson_pmf(a, l_away)

        p_home = np.sum(np.tril(matrix, -1))
        p_btts = 1 - (np.sum(matrix[0, :]) + np.sum(matrix[:, 0]) - matrix[0,0])
        
        # Elegir pick base
        pick = f"Gana {game['home']}" if p_home > 0.55 else "Ambos Anotan" if p_btts > 0.55 else "Over 2.5"
        
        return {
            "pick": pick,
            "prob": p_home if "Gana" in pick else p_btts,
            "ev": round(((p_home if "Gana" in pick else p_btts) * h_dec) - 1, 2),
            "h_dec": h_dec
        }

    def simulate_parlay_profit(self, picks, monto):
        cuota_total = 1.0
        for p in picks:
            # Intentar obtener cuota del pick, si no usar 1.80 por defecto
            cuota_total *= 1.85 
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago, 2),
            "ganancia_neta": round(pago - monto, 2)
        }
