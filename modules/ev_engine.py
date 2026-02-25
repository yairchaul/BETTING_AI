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
        self.high_prob_threshold = 0.88   # 88% para priorizar fuertemente

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            partido = f"{g.get('home','')} vs {g.get('away','')}"
            
            lambda_home = 1.68
            lambda_away = 1.05
            
            # Boost fuerte para favoritos claros
            try:
                home_odd = float(g.get("home_odd", 200))
                if home_odd < 150: lambda_home += 0.65
                elif home_odd < 200: lambda_home += 0.35
            except: pass
            
            p_home, p_draw, p_away = get_poisson_probs(lambda_home, lambda_away)
            expected_total = lambda_home + lambda_away
            
            # Probabilidades de mercados adicionales
            prob_btts = 0.0
            prob_over_1_5 = 0.0
            prob_over_2_5 = 0.0
            for h in range(10):
                for a in range(10):
                    if h > 0 and a > 0: prob_btts += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
                    if h + a > 1.5: prob_over_1_5 += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
                    if h + a > 2.5: prob_over_2_5 += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
            
            # Cascada de decisión por partido
            options = []
            
            # 1. Over 1.5 Primer Tiempo (prioridad máxima)
            prob_over_1t = prob_over_1_5 * 0.48  # aproximación realista para 1T
            if prob_over_1t >= 0.68:
                options.append(("Over 1.5 1T", prob_over_1t, 1.85))
            
            # 2. BTTS
            if prob_btts >= 0.62:
                options.append(("Ambos Equipos Anotan", prob_btts, 1.90))
            
            # 3. Over 2.5
            if prob_over_2_5 >= 0.58:
                options.append(("Over 2.5", prob_over_2_5, 1.90))
            
            # 4. Ganador (si ninguna de las anteriores es fuerte)
            for outcome, model_p, odds_key in [
                ("home", p_home, "home_odd"),
                ("draw", p_draw, "draw_odd"),
                ("away", p_away, "away_odd")
            ]:
                odds_str = g.get(odds_key)
                if odds_str:
                    odds = float(odds_str)
                    ev = calculate_ev(model_p, odds)
                    if ev > self.min_ev_threshold:
                        pick_name = f"{g['home']} gana" if outcome=="home" else "Empate" if outcome=="draw" else f"{g['away']} gana"
                        options.append((pick_name, model_p, odds))
            
            # Elegir la mejor opción del partido
            if options:
                best = max(options, key=lambda x: x[1])  # mayor probabilidad
                pick_name, prob, cuota = best
                resultados.append({
                    "partido": partido,
                    "pick": pick_name,
                    "probabilidad": round(prob*100, 1),
                    "cuota": str(cuota) if isinstance(cuota, (int,float)) else cuota,
                    "ev": round(calculate_ev(prob, float(cuota) if isinstance(cuota, (int,float)) else 1.9), 3),
                    "razon": f"Opción ganadora de la cascada (Prob: {prob*100:.1f}%)",
                    "expected_total": round(expected_total, 1)
                })

        # Mejor por partido + ordenar por EV
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
