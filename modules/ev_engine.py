# modules/ev_engine.py
import math
import streamlit as st
from collections import defaultdict
from modules.ev_scanner import american_to_probability, calculate_ev
from modules.stats_fetch import get_last_5_matches, get_injuries

# ... (mantén las funciones poisson_pmf y get_poisson_probs igual que antes)

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.09   # más exigente
        self.max_odds_allowed = 250    # NO acepta cuotas > +250 a menos que EV sea brutal

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            # Si es 1X2
            if g.get("market") == "1X2":
                last_home = get_last_5_matches(g["home"])
                inj_home = get_injuries(g["home"])
                last_away = get_last_5_matches(g["away"])
                inj_away = get_injuries(g["away"])
                
                lambda_home = 1.58   # mayor ventaja local en Liga MX
                lambda_away = 1.12
                
                # Ajustes fuertes
                if any(word in str(i).lower() for i in inj_away for word in ["ankle","knee","hamstring","defensa"]):
                    lambda_home += 0.45
                if any(word in str(i).lower() for i in inj_home for word in ["ankle","knee","hamstring","defensa"]):
                    lambda_away += 0.45
                
                if last_home:
                    recent = sum(int(m.get('score','0-0').split('-')[0]) for m in last_home if '-' in m.get('score','')) / max(len(last_home),1)
                    lambda_home = (lambda_home * 0.45) + (recent * 0.55)
                if last_away:
                    recent_conceded = sum(int(m.get('score','0-0').split('-')[1]) for m in last_away if '-' in m.get('score','')) / max(len(last_away),1)
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
                        continue  # FILTRO FUERTE: descarta underdogs locos
                    
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

            # Futuro: Over/Under (cuando vision_reader lo detecte)
            elif "Over/Under" in str(g.get("market", "")):
                # Aquí iría lógica de Over 2.5 si expected_total > 2.75
                pass

        # === FILTRO FINAL: 1 mejor pick por partido ===
        picks_by_match = defaultdict(list)
        for r in resultados:
            picks_by_match[r["partido"]].append(r)
        
        best_picks = [max(picks, key=lambda x: x["ev"]) for picks in picks_by_match.values()]
        best_picks.sort(key=lambda x: x["ev"], reverse=True)
        
        parlay = best_picks[:4]  # máximo 4 legs (más seguro)

        return resultados, parlay

    # simulate_parlay_profit se mantiene igual
