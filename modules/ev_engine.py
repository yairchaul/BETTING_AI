import math

def poisson_pmf(k, lam):
    if lam <= 0: return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.05

    def get_best_ev_pick(self, game):
        # 1. Convertir momios a probabilidad implícita y calcular Lambdas (goles)
        try:
            h_odd_val = float(str(game['home_odd']).replace('+', '').strip())
            # Convertir momio a decimal para cálculos
            h_dec = (h_odd_val/100 + 1) if h_odd_val > 0 else (100/abs(h_odd_val) + 1)
            prob_implied_h = 1 / h_dec
            
            # Ajuste dinámico de Goles Esperados (Lambda) según momio
            # Si el momio es muy negativo (favorito), subimos su lambda
            l_home = 2.5 * prob_implied_h + 0.5
            l_away = 1.2 * (1 - prob_implied_h) + 0.3
        except:
            l_home, l_away = 1.5, 1.2

        # 2. Calcular Probabilidades Reales usando Poisson
        p_home = p_draw = p_away = 0.0
        p_btts_no = poisson_pmf(0, l_home) + poisson_pmf(0, l_away) # Simplificado
        p_over_2_5 = 1 - sum([poisson_pmf(h, l_home)*poisson_pmf(a, l_away) 
                            for h in range(3) for a in range(3) if h+a < 2.5])

        for h in range(8):
            for a in range(8):
                prob = poisson_pmf(h, l_home) * poisson_pmf(a, l_away)
                if h > a: p_home += prob
                elif h == a: p_draw += prob
                else: p_away += prob

        # 3. Lógica de Decisión (Criterio de Valor)
        # Solo sugerimos BTTS si ambos lambdas son cercanos y > 1.2
        if l_home > 2.2 and l_away < 0.8:
            pick, prob_final = f"{game['home']} gana", p_home
        elif l_away > 2.2 and l_home < 0.8:
            pick, prob_final = f"{game['away']} gana", p_away
        elif p_over_2_5 > 0.65:
            pick, prob_final = "Altas (Over 2.5)", p_over_2_5
        else:
            pick, prob_final = "Ambos Anotan (BTTS)", (1 - p_btts_no/2)

        return {
            "partido": f"{game['home']} vs {game['away']}",
            "pick": pick,
            "prob": round(prob_final * 100, 1),
            "cuota": game['home_odd'] if "gana" in pick else "-110"
        }

    def simulate_parlay_profit(self, picks, monto):
        cuota_total = 1.0
        for p in picks:
            val = float(str(p["cuota"]).replace('+', '').strip())
            decimal = (val/100 + 1) if val > 0 else (100/abs(val) + 1)
            cuota_total *= decimal
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago, 2),
            "ganancia_neta": round(pago - monto, 2)
        }
