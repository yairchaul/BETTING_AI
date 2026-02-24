# modules/ev_engine.py
import math
from collections import defaultdict
from modules.ev_scanner import american_to_probability, calculate_ev
from modules.stats_fetch import get_last_5_matches, get_injuries

# ────────────────────────────────────────────────
# Funciones auxiliares Poisson (deben estar ANTES de la clase)
# ────────────────────────────────────────────────

def poisson_pmf(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
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
    if total == 0: return 0.333, 0.334, 0.333  # fallback muy raro
    return p_home / total, p_draw / total, p_away / total

# ────────────────────────────────────────────────
# Clase principal
# ────────────────────────────────────────────────

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.09
        self.max_odds_allowed = 250

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            # Solo procesamos 1X2 por ahora (Over/Under en próximo paso)
            if g.get("market") != "1X2":
                continue
            
            last_home = get_last_5_matches(g["home"])
            inj_home = get_injuries(g["home"])
            last_away = get_last_5_matches(g["away"])
            inj_away = get_injuries(g["away"])
            
            lambda_home = 1.58
            lambda_away = 1.12
            
            if any(word in str(i).lower() for i in inj_away for word in ["ankle","knee","hamstring","defensa","defender"]):
                lambda_home += 0.45
            if any(word in str(i).lower() for i in inj_home for word in ["ankle","knee","hamstring","defensa","defender"]):
                lambda_away += 0.45
            
            if last_home:
                recent = sum(int(m.get('score','0-0').split('-')[0]) for m in last_home if '-' in m.get('score','')) / max(1, len(last_home))
                lambda_home = (lambda_home * 0.45) + (recent * 0.55)
            if last_away:
                recent_conceded = sum(int(m.get('score','0-0').split('-')[1]) for m in last_away if '-' in m.get('score','')) / max(1, len(last_away))
                lambda_away = (lambda_away * 0.45) + (recent_conceded * 0.55)
            
            p_home, p_draw, p_away = get_poisson_probs(lambda_home, lambda_away)
            expected_total = lambda_home + lambda_away
            
            for outcome, odds_key, model_p in [
                ("home", "home_odd", p_home),
                ("draw", "draw_odd", p_draw),
                ("away", "away_odd", p_away)
            ]:
                odds_str = g.get(odds_key)
                if not odds_str or not str(odds_str).strip(): continue
                try:
                    odds = float(odds_str)
                except: continue
                
                if odds > self.max_odds_allowed and model_p < 0.48:
                    continue  # filtro anti-underdog extremo
                
                ev = calculate_ev(model_p, odds)
                
                if ev > self.min_ev_threshold:
                    pick_name = f"{g['home']} gana" if outcome=="home" else "Empate" if outcome=="draw" else f"{g['away']} gana"
                    razon = f"λH {lambda_home:.2f} | λA {lambda_away:.2f} | Goles esperados: {expected_total:.1f}"
                    
                    resultados.append({
                        "partido": f"{g['home']} vs {g['away']}",
                        "pick": pick_name,
                        "probabilidad": round(model_p*100, 1),
                        "cuota": odds_str,
                        "ev": round(ev, 3),
                        "razon": razon,
                        "expected_total": round(expected_total, 1),
                        "market": "1X2"
                    })

        picks_by_match = defaultdict(list)
        for r in resultados:
            picks_by_match[r["partido"]].append(r)
        
        best_picks = [max(picks, key=lambda x: x["ev"]) for picks in picks_by_match.values()]
        best_picks.sort(key=lambda x: x["ev"], reverse=True)
        
        parlay = best_picks[:4]  # máximo 4 legs

        return resultados, parlay

    def simulate_parlay_profit(self, parlay: list, monto: float):
        if not parlay:
            return {"cuota_total": 1.0, "pago_total": monto, "ganancia_neta": 0.0}
        
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
