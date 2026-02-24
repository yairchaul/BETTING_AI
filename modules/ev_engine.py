# modules/ev_engine.py
import math
from collections import defaultdict
from modules.ev_scanner import american_to_probability, calculate_ev
from modules.stats_fetch import get_last_5_matches, get_injuries

def poisson_pmf(k, lam):
    if lam <= 0: return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def get_poisson_probs(lambda_home: float, lambda_away: float):
    max_goals = 9
    p_home = p_draw = p_away = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
            if h > a: p_home += prob
            elif h == a: p_draw += prob
            else: p_away += prob
    total = p_home + p_draw + p_away
    if total == 0: return 0.333, 0.334, 0.333
    return p_home / total, p_draw / total, p_away / total

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.14
        self.max_odds_allowed = 150  # ahora sí limita cuotas altas

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            partido = f"{g.get('home','')} vs {g.get('away','')}"
            market = g.get("market", "1X2")
            
            if market == "1X2":
                lambda_home = 1.70
                lambda_away = 1.05
                
                try:
                    home_odd = float(g.get("home_odd", 200))
                    if home_odd < -100: lambda_home += 0.80  # favoritos pesados
                    elif home_odd < 100: lambda_home += 0.50
                    elif home_odd < 200: lambda_home += 0.25
                except: pass
                
                p_home, p_draw, p_away = get_poisson_probs(lambda_home, lambda_away)
                expected_total = lambda_home + lambda_away
                
                for outcome, odds_key, model_p in [("home","home_odd",p_home), ("draw","draw_odd",p_draw), ("away","away_odd",p_away)]:
                    odds_str = g.get(odds_key)
                    if not odds_str: continue
                    odds = float(odds_str)
                    
                    # Penalización fuerte a cuotas altas
                    adjusted_ev = calculate_ev(model_p, odds)
                    if odds > 150: adjusted_ev *= 0.7  # reduce EV en 30%
                    if odds > self.max_odds_allowed: continue
                    
                    if adjusted_ev > self.min_ev_threshold:
                        pick_name = f"{g['home']} gana" if outcome=="home" else "Empate" if outcome=="draw" else f"{g['away']} gana"
                        resultados.append({
                            "partido": partido,
                            "pick": pick_name,
                            "probabilidad": round(model_p*100, 1),
                            "cuota": odds_str,
                            "ev": round(adjusted_ev, 3),
                            "razon": f"Goles esperados: {expected_total:.1f}",
                            "expected_total": round(expected_total, 1),
                            "market": "1X2"
                        })
            
            # Recomendación Over/BTTS
            if expected_total > 2.8:
                prob_over_2_5 = 0.0
                for h in range(10):
                    for a in range(10):
                        if h + a > 2.5:
                            prob_over_2_5 += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
                ev_over = calculate_ev(prob_over_2_5, 1.85)
                if ev_over > self.min_ev_threshold:
                    resultados.append({
                        "partido": partido,
                        "pick": "Over 2.5",
                        "probabilidad": round(prob_over_2_5*100, 1),
                        "cuota": "1.85",
                        "ev": round(ev_over, 3),
                        "razon": "Alta probabilidad de goles",
                        "expected_total": round(expected_total, 1),
                        "market": "Over"
                    })

        picks_by_match = defaultdict(list)
        for r in resultados:
            picks_by_match[r["partido"]].append(r)
        
        best_picks = [max(picks, key=lambda x: x["ev"]) for picks in picks_by_match.values()]
        best_picks.sort(key=lambda x: x["ev"], reverse=True)
        parlay = best_picks[:5]
        return resultados, parlay

    def simulate_parlay_profit(self, parlay: list, monto: float):
        if not parlay: return {"cuota_total": 1.0, "pago_total": monto, "ganancia_neta": 0.0}
        cuota_total = 1.0
        for p in parlay:
            odds = float(p["cuota"])
            decimal = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1
            cuota_total *= decimal
        pago_total = monto * cuota_total
        ganancia_neta = pago_total - monto
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago_total, 2),
            "ganancia_neta": round(ganancia_neta, 2)
        }
