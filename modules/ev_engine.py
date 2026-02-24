# modules/ev_engine.py

# modules/ev_engine.py
import math
from collections import defaultdict
from modules.ev_scanner import american_to_probability, calculate_ev

def poisson_pmf(k, lam):
    if lam == 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def get_poisson_probs(lambda_home: float, lambda_away: float):
    """Devuelve (p_home, p_draw, p_away) con Poisson puro"""
    max_goals = 9
    p_home = p_draw = p_away = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
            if h > a:
                p_home += prob
            elif h == a:
                p_draw += prob
            else:
                p_away += prob
    total = p_home + p_draw + p_away
    return p_home/total, p_draw/total, p_away/total

# ====================== FUERZA POR EQUIPO (lambdas reales) ======================
TEAM_STRENGTH = {
    # Eredivisie (ejemplo PSV vs AZ)
    "PSV Eindhoven": {"attack": 2.45, "defense": 0.85},
    "AZ Alkmaar": {"attack": 1.65, "defense": 1.35},
    
    # Liga MX (agrega los que más uses)
    "América": {"attack": 1.85, "defense": 1.05},
    "Tigres UANL": {"attack": 1.95, "defense": 0.95},
    "Monterrey": {"attack": 1.75, "defense": 1.10},
    "Chivas Guadalajara": {"attack": 1.55, "defense": 1.20},
    "Pachuca": {"attack": 1.70, "defense": 1.25},
    "Cruz Azul": {"attack": 1.80, "defense": 1.15},
    # ... agrega más según vayas probando
}

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.06   # subimos un poco el filtro de valor

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            # === LAMBDA POR EQUIPO (el corazón del modelo profesional) ===
            home_str = TEAM_STRENGTH.get(g["home"], {"attack": 1.45, "defense": 1.20})
            away_str = TEAM_STRENGTH.get(g["away"], {"attack": 1.35, "defense": 1.30})
            
            lambda_home = home_str["attack"] * away_str["defense"]
            lambda_away = away_str["attack"] * home_str["defense"]
            
            p_home, p_draw, p_away = get_poisson_probs(lambda_home, lambda_away)
            expected_total = lambda_home + lambda_away
            
            # Análisis paso a paso para cada outcome
            for outcome, odds_key, model_p in [
                ("home", "home_odd", p_home),
                ("draw", "draw_odd", p_draw),
                ("away", "away_odd", p_away)
            ]:
                odds_str = g.get(odds_key)
                if not odds_str or str(odds_str).strip() == "":
                    continue
                try:
                    odds = float(odds_str)
                except:
                    continue
                
                ev = calculate_ev(model_p, odds)
                
                if ev > self.min_ev_threshold:
                    pick_name = (
                        f"{g['home']} gana" if outcome == "home" else
                        "Empate" if outcome == "draw" else
                        f"{g['away']} gana"
                    )
                    
                    razon = (f"λH {lambda_home:.2f} | λA {lambda_away:.2f} | "
                             f"Total esperados: {expected_total:.1f} goles | "
                             f"Prob modelo: {model_p*100:.1f}%")
                    
                    resultados.append({
                        "partido": f"{g['home']} vs {g['away']}",
                        "pick": pick_name,
                        "probabilidad": round(model_p * 100, 1),
                        "cuota": odds_str,
                        "ev": round(ev, 3),
                        "razon": razon,
                        "expected_total": round(expected_total, 1)
                    })

        # === FILTRO: MÁXIMO 1 PICK POR PARTIDO (el de mayor EV) ===
        picks_by_match = defaultdict(list)
        for r in resultados:
            picks_by_match[r["partido"]].append(r)
        
        best_picks = []
        for match_picks in picks_by_match.values():
            best = max(match_picks, key=lambda x: x["ev"])
            best_picks.append(best)
        
        best_picks.sort(key=lambda x: x["ev"], reverse=True)
        parlay = best_picks[:5]   # máximo 5 legs

        return resultados, parlay

    def simulate_parlay_profit(self, parlay: list, monto: float):
        if not parlay:
            return {"cuota_total": 1.0, "pago_total": monto, "ganancia_neta": 0.0}
        
        cuota_total = 1.0
        for p in parlay:
            decimal = american_to_decimal(p["cuota"]) if "american_to_decimal" in globals() else (float(p["cuota"])/100 + 1 if float(p["cuota"]) > 0 else 100/abs(float(p["cuota"])) + 1)
            cuota_total *= decimal
        
        pago_total = monto * cuota_total
        ganancia_neta = pago_total - monto
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago_total, 2),
            "ganancia_neta": round(ganancia_neta, 2)
        }

def american_to_decimal(odds):
    odds = float(odds)
    return odds/100 + 1 if odds > 0 else 100/abs(odds) + 1

