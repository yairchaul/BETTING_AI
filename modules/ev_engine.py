# modules/ev_engine.py
# modules/ev_engine.py
import math
import requests
import streamlit as st
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
    return p_home/total, p_draw/total, p_away/total

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.08   # subimos un poco para ser más selectivos

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            last_home = get_last_5_matches(g["home"])
            inj_home = get_injuries(g["home"])
            last_away = get_last_5_matches(g["away"])
            inj_away = get_injuries(g["away"])
            
            # Lambdas más realistas para fútbol promedio 2026
            lambda_home = 1.52
            lambda_away = 1.18
            
            # Ajustes por lesiones y forma (más fuertes)
            if any(word in str(i).lower() for i in inj_away for word in ["ankle","knee","hamstring","defensa","defender"]):
                lambda_home += 0.40
            if any(word in str(i).lower() for i in inj_home for word in ["ankle","knee","hamstring","defensa","defender"]):
                lambda_away += 0.40
            
            # Forma reciente más pesada
            if last_home:
                recent_home = sum(int(m.get('score','0-0').split('-')[0]) for m in last_home if '-' in m.get('score','')) / max(len(last_home),1)
                lambda_home = (lambda_home * 0.5) + (recent_home * 0.5)
            if last_away:
                recent_away_conceded = sum(int(m.get('score','0-0').split('-')[1]) for m in last_away if '-' in m.get('score','')) / max(len(last_away),1)
                lambda_away = (lambda_away * 0.5) + (recent_away_conceded * 0.5)
            
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
                
                ev = calculate_ev(model_p, odds)
                
                if ev > self.min_ev_threshold:
                    pick_name = f"{g['home']} gana" if outcome=="home" else "Empate" if outcome=="draw" else f"{g['away']} gana"
                    
                    razon = (f"λH {lambda_home:.2f} | λA {lambda_away:.2f} | "
                             f"Goles esperados: {expected_total:.1f} | "
                             f"Lesiones: {len(inj_away)} visitante / {len(inj_home)} local")
                    
                    resultados.append({
                        "partido": f"{g['home']} vs {g['away']}",
                        "pick": pick_name,
                        "probabilidad": round(model_p*100, 1),
                        "cuota": odds_str,
                        "ev": round(ev, 3),
                        "razon": razon,
                        "expected_total": round(expected_total, 1)
                    })

        # === FILTRO FINAL: 1 pick por partido + ordenado por EV descendente ===
        picks_by_match = defaultdict(list)
        for r in resultados:
            picks_by_match[r["partido"]].append(r)
        
        best_picks = [max(picks, key=lambda x: x["ev"]) for picks in picks_by_match.values()]
        best_picks.sort(key=lambda x: x["ev"], reverse=True)
        
        parlay = best_picks[:5]   # máximo 5 legs

        return resultados, parlay

    def simulate_parlay_profit(self, parlay: list, monto: float):
        if not parlay: 
            return {"cuota_total": 1.0, "pago_total": monto, "ganancia_neta": 0.0}
        
        cuota_total = 1.0
        for p in parlay:
            odds = float(p["cuota"])
            decimal = odds/100 + 1 if odds > 0 else 100/abs(odds) + 1
            cuota_total *= decimal
        
        pago_total = monto * cuota_total
        ganancia_neta = pago_total - monto
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago_total, 2),
            "ganancia_neta": round(ganancia_neta, 2)
        }
