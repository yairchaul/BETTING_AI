# modules/ev_engine.py
import math
from collections import defaultdict
from modules.ev_scanner import american_to_probability, calculate_ev
from modules.stats_fetch import get_last_5_matches, get_injuries

# ────────────────────────────────────────────────
# Funciones auxiliares Poisson (obligatorias antes de la clase)
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
    if total == 0: return 0.333, 0.334, 0.333  # fallback raro
    return p_home / total, p_draw / total, p_away / total

# ────────────────────────────────────────────────
# Clase principal
# ────────────────────────────────────────────────

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.09
        self.max_odds_allowed = 250  # límite anti-underdog extremo

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            market_type = g.get("market", "1X2")
            partido = f"{g.get('home', 'Equipo A')} vs {g.get('away', 'Equipo B')}"
            
            # ─── 1. Procesar 1X2 ────────────────────────────────────────
            if market_type == "1X2":
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
                        continue
                    
                    ev = calculate_ev(model_p, odds)
                    
                    if ev > self.min_ev_threshold:
                        pick_name = f"{g['home']} gana" if outcome=="home" else "Empate" if outcome=="draw" else f"{g['away']} gana"
                        razon = f"λH {lambda_home:.2f} | λA {lambda_away:.2f} | Goles esperados: {expected_total:.1f}"
                        
                        resultados.append({
                            "partido": partido,
                            "pick": pick_name,
                            "probabilidad": round(model_p*100, 1),
                            "cuota": odds_str,
                            "ev": round(ev, 3),
                            "razon": razon,
                            "expected_total": round(expected_total, 1),
                            "market": "1X2"
                        })
            
            # ─── 2. Procesar Over/Under ─────────────────────────────────
            elif "Over/Under" in market_type:
                line = float(g.get("line", 2.5))
                odd = float(g.get("odd", 0))
                o_type = g.get("type", "Over")
                
                # Probabilidad aproximada de Over con Poisson
                prob_over = 0.0
                for h in range(10):
                    for a in range(10):
                        if (h + a) > line:
                            prob_over += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
                
                ev_over = calculate_ev(prob_over, odd) if o_type == "Over" else calculate_ev(1 - prob_over, odd)
                
                if ev_over > self.min_ev_threshold:
                    pick_name = f"{o_type} {line}"
                    razon = f"Goles esperados: {expected_total:.1f} → Prob {o_type}: {prob_over*100:.1f}%"
                    
                    resultados.append({
                        "partido": partido,
                        "pick": pick_name,
                        "probabilidad": round(prob_over*100 if o_type=="Over" else (1-prob_over)*100, 1),
                        "cuota": str(odd),
                        "ev": round(ev_over, 3),
                        "razon": razon,
                        "expected_total": round(expected_total, 1),
                        "market": market_type
                    })

        # Filtro final: 1 mejor pick por partido (mayor EV)
        picks_by_match = defaultdict(list)
        for r in resultados:
            picks_by_match[r["partido"]].append(r)
        
        best_picks = [max(picks, key=lambda x: x["ev"]) for picks in picks_by_match.values()]
        best_picks.sort(key=lambda x: x["ev"], reverse=True)
        
        parlay = best_picks[:4]

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
