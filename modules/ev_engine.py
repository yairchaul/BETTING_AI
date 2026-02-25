import math
import numpy as np

class EVEngine:
    def poisson_pmf(self, k, lam):
        if lam <= 0: return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)

    def get_raw_probabilities(self, game):
        """Busca el mercado con mayor valor (Edge) en cascada."""
        try:
            # Procesamiento de momios (Americano a Decimal)
            h_odd_str = str(game.get('home_odd', '100')).replace('+', '').strip()
            h_odd = float(h_odd_str) if h_odd_str else 100.0
            h_dec = (h_odd/100 + 1) if h_odd > 0 else (100/abs(h_odd) + 1)
            prob_implied = 1 / h_dec

            # Proyección de goles (Lambdas)
            l_home = 2.4 * prob_implied
            l_away = 1.3 * (1 - prob_implied)

            # Matriz de Poisson 7x7
            matrix = np.zeros((7, 7))
            for h in range(7):
                for a in range(7):
                    matrix[h, a] = self.poisson_pmf(h, l_home) * self.poisson_pmf(a, l_away)

            # Probabilidades de Mercados
            p_home = np.sum(np.tril(matrix, -1))
            p_btts = 1 - (np.sum(matrix[0, :]) + np.sum(matrix[:, 0]) - matrix[0,0])
            p_over_2_5 = 1 - sum([matrix[h, a] for h in range(7) for a in range(7) if h+a <= 2.5])

            # --- LÓGICA DE CASCADA DE VALOR ---
            # Comparamos contra cuotas de referencia para hallar el EDGE real
            opciones = [
                {"pick": f"Gana {game['home']}", "prob": p_home, "edge": p_home - prob_implied},
                {"pick": "Ambos Anotan", "prob": p_btts, "edge": p_btts - 0.52},
                {"pick": "Over 2.5 Goles", "prob": p_over_2_5, "edge": p_over_2_5 - 0.50}
            ]
            
            # Elegir el que tiene mayor ventaja estadística
            mejor = max(opciones, key=lambda x: x['edge'])

            return {
                "pick": mejor['pick'],
                "prob": mejor['prob'],
                "ev": round(mejor['edge'], 3), # Edge real
                "cuota_ref": round(h_dec, 2)
            }
        except Exception:
            return {"pick": "Analizar Over 1.5", "prob": 0.6, "ev": 0.1, "cuota_ref": 1.50}

    def simulate_parlay_profit(self, picks, monto):
        """Cálculos finales con limpieza absoluta de decimales."""
        cuota_total = 1.0
        for p in picks:
            cuota_total *= float(p.get('cuota_ref', 1.80))
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago, 2),
            "ganancia_neta": round(pago - monto, 2),
            "monto_invertido": round(monto, 2)
        }
