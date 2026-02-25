import math
from modules.ev_scanner import calculate_ev

def poisson_pmf(k, lam):
    if lam <= 0: return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def get_poisson_probs(lambda_home, lambda_away):
    max_goals = 8
    p_home = p_draw = p_away = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
            if h > a: p_home += prob
            elif h == a: p_draw += prob
            else: p_away += prob
    total = p_home + p_draw + p_away
    return p_home/total, p_draw/total, p_away/total

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.13

    def build_parlay(self, games):
        resultados = []
        for g in games:
            partido = f"{g.get('home','')} vs {g.get('away','')}"
            
            # Ajuste de lambdas según momios del OCR
            l_home, l_away = 1.65, 1.20
            try:
                h_odd = float(str(g.get("home_odd", "0")).replace('+', '').strip())
                if h_odd < 0: l_home += 0.7 # Favorito claro
            except: pass

            ph, pd, pa = get_poisson_probs(l_home, l_away)
            
            p_over_1_5 = 1 - (poisson_pmf(0, l_home)*poisson_pmf(0, l_away) + 
                             poisson_pmf(1, l_home)*poisson_pmf(0, l_away) + 
                             poisson_pmf(0, l_home)*poisson_pmf(1, l_away))
            p_btts = (1 - poisson_pmf(0, l_home)) * (1 - poisson_pmf(0, l_away))
            p_over_1t = p_over_1_5 * 0.42
            p_over_2_5 = p_over_1_5 * 0.75

            # --- CASCADA ---
            if p_over_1t >= 0.68:
                chosen = {"pick": "Over 1.5 1T", "prob": p_over_1t, "cuota": 1.85}
            elif p_btts >= 0.62:
                chosen = {"pick": "Ambos Equipos Anotan", "prob": p_btts, "cuota": 1.75}
            elif p_over_2_5 >= 0.58:
                chosen = {"pick": "Over 2.5", "prob": p_over_2_5, "cuota": 1.80}
            else:
                opts = [(f"{g['home']} gana", ph), ("Empate", pd), (f"{g['away']} gana", pa)]
                best_o, best_p = max(opts, key=lambda x: x[1])
                chosen = {"pick": best_o, "prob": best_p, "cuota": g.get("home_odd") if "gana" in best_o else "+280"}

            resultados.append({
                "partido": partido,
                "pick": chosen["pick"],
                "probabilidad": round(chosen["prob"] * 100, 1),
                "cuota": str(chosen["cuota"]),
                "ev": round(calculate_ev(chosen["prob"], 1.80), 3)
            })

        parlay = sorted(resultados, key=lambda x: x["probabilidad"], reverse=True)[:5]
        return resultados, parlay

    def simulate_parlay_profit(self, parlay, monto):
        cuota_total = 1.0
        for p in parlay:
            try:
                val = float(str(p["cuota"]).replace('+', '').strip())
                # Conversión real: si es positivo (ej +150) o negativo (ej -200)
                decimal = (val/100 + 1) if val > 0 else (100/abs(val) + 1)
                cuota_total *= decimal
            except: 
                cuota_total *= 1.85 # Valor fallback
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago, 2),
            "ganancia_neta": round(pago - monto, 2)
        }

