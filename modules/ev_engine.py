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
        self.min_ev_threshold = 0.13

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            partido = f"{g.get('home','')} vs {g.get('away','')}"
            
            # Calcular lambdas
            lambda_home = 1.65
            lambda_away = 1.08
            try:
                if float(g.get("home_odd", 200)) < 150:
                    lambda_home += 0.60
            except: pass
            
            p_home, p_draw, p_away = get_poisson_probs(lambda_home, lambda_away)
            expected_total = lambda_home + lambda_away
            
            # 1X2
            for outcome, odds_key, model_p in [
                ("home", "home_odd", p_home),
                ("draw", "draw_odd", p_draw),
                ("away", "away_odd", p_away)
            ]:
                odds_str = g.get(odds_key)
                if not odds_str: continue
                odds = float(odds_str)
                ev = calculate_ev(model_p, odds)
                if ev > self.min_ev_threshold:
                    pick_name = f"{g['home']} gana" if outcome=="home" else "Empate" if outcome=="draw" else f"{g['away']} gana"
                    resultados.append({
                        "partido": partido,
                        "pick": pick_name,
                        "probabilidad": round(model_p*100, 1),
                        "cuota": odds_str,
                        "ev": round(ev, 3),
                        "razon": f"Goles esperados: {expected_total:.1f}",
                        "expected_total": round(expected_total, 1)
                    })
            
            # BTTS (Ambos anotan)
            prob_btts = 0.0
            for h in range(10):
                for a in range(10):
                    if h > 0 and a > 0:
                        prob_btts += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
            ev_btts = calculate_ev(prob_btts, 1.90)  # cuota típica
            if ev_btts > self.min_ev_threshold:
                resultados.append({
                    "partido": partido,
                    "pick": "Ambos Equipos Anotan",
                    "probabilidad": round(prob_btts*100, 1),
                    "cuota": "1.90",
                    "ev": round(ev_btts, 3),
                    "razon": f"Prob BTTS: {prob_btts*100:.1f}%",
                    "expected_total": round(expected_total, 1)
                })
            
            # Over 1.5 y Over 2.5
            prob_over_1_5 = 0.0
            prob_over_2_5 = 0.0
            for h in range(10):
                for a in range(10):
                    if h + a > 1.5: prob_over_1_5 += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
                    if h + a > 2.5: prob_over_2_5 += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
            
            for line, prob, name in [(1.5, prob_over_1_5, "Over 1.5"), (2.5, prob_over_2_5, "Over 2.5")]:
                ev_over = calculate_ev(prob, 1.75 if line == 1.5 else 1.90)
                if ev_over > self.min_ev_threshold and expected_total > (1.8 if line == 1.5 else 2.6):
                    resultados.append({
                        "partido": partido,
                        "pick": name,
                        "probabilidad": round(prob*100, 1),
                        "cuota": "1.75" if line == 1.5 else "1.90",
                        "ev": round(ev_over, 3),
                        "razon": f"Goles esperados: {expected_total:.1f}",
                        "expected_total": round(expected_total, 1)
                    })

        # Mejor opción por partido
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
