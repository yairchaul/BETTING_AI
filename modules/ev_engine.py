# modules/ev_engine.py
import math
import requests
import streamlit as st
from collections import defaultdict
from modules.ev_scanner import american_to_probability, calculate_ev
from modules.stats_fetch import get_last_5_matches, get_injuries

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
    return p_home / total, p_draw / total, p_away / total

def get_api_odds(home_team: str, away_team: str):
    """Usa The Odds API (endpoint universal /upcoming) - 1 sola petición"""
    api_key = st.secrets.get("ODDS_API_KEY")
    if not api_key:
        return None
    try:
        url = (
            "https://api.the-odds-api.com/v4/sports/upcoming/odds?"
            f"apiKey={api_key}&regions=us,uk,eu&markets=h2h&oddsFormat=american"
        )
        r = requests.get(url, timeout=12)
        if r.status_code != 200:
            return None
        
        data = r.json()
        for event in data:
            h = event.get("home_team", "").lower()
            a = event.get("away_team", "").lower()
            if (home_team.lower() in h and away_team.lower() in a) or \
               (away_team.lower() in h and home_team.lower() in a):
                # Extraer mejores odds 1X2
                best_home = best_draw = best_away = None
                for bm in event.get("bookmakers", []):
                    for mkt in bm.get("markets", []):
                        if mkt.get("key") == "h2h":
                            for out in mkt.get("outcomes", []):
                                name = out.get("name", "")
                                price = out.get("price")
                                if name == event.get("home_team"):
                                    best_home = max(best_home or -999, price)
                                elif name == "Draw":
                                    best_draw = max(best_draw or -999, price)
                                elif name == event.get("away_team"):
                                    best_away = max(best_away or -999, price)
                return {
                    "home_odd_api": best_home,
                    "draw_odd_api": best_draw,
                    "away_odd_api": best_away,
                    "commence_time": event.get("commence_time")
                }
        return None
    except:
        return None

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.06

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            # Datos dinámicos (sin hardcodear nada)
            last_home = get_last_5_matches(g["home"])
            inj_home = get_injuries(g["home"])
            last_away = get_last_5_matches(g["away"])
            inj_away = get_injuries(g["away"])
            
            # Lambda universal + ajustes
            lambda_home = 1.48
            lambda_away = 1.15
            
            # Ajuste por lesiones defensa
            if any(word in i.lower() for i in inj_away for word in ["ankle", "knee", "hamstring", "defender", "defensa"]):
                lambda_home += 0.35
            if any(word in i.lower() for i in inj_home for word in ["ankle", "knee", "hamstring", "defender", "defensa"]):
                lambda_away += 0.35
            
            # Ajuste por forma reciente (últimos 5)
            if last_home and len(last_home) > 0:
                recent_home = sum(int(m.get('score','0-0').split('-')[0]) for m in last_home if '-' in m.get('score','')) / len(last_home)
                lambda_home = (lambda_home * 0.6) + (recent_home * 0.4)
            if last_away and len(last_away) > 0:
                recent_away_conceded = sum(int(m.get('score','0-0').split('-')[1]) for m in last_away if '-' in m.get('score','')) / len(last_away)
                lambda_away = (lambda_away * 0.6) + (recent_away_conceded * 0.4)
            
            p_home, p_draw, p_away = get_poisson_probs(lambda_home, lambda_away)
            expected_total = lambda_home + lambda_away
            
            # Enriquecimiento con The Odds API (universal)
            api_odds = get_api_odds(g["home"], g["away"])
            
            for outcome, odds_key, model_p in [
                ("home", "home_odd", p_home),
                ("draw", "draw_odd", p_draw),
                ("away", "away_odd", p_away)
            ]:
                odds_str = g.get(odds_key)
                if not odds_str or not str(odds_str).strip():
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
                             f"Goles esperados: {expected_total:.1f} | "
                             f"Lesiones: {len(inj_away)} visitante / {len(inj_home)} local | "
                             f"Forma reciente aplicada")
                    
                    if api_odds:
                        razon += f" | API Odds encontrado: {api_odds.get('commence_time','')}"
                    
                    resultados.append({
                        "partido": f"{g['home']} vs {g['away']}",
                        "pick": pick_name,
                        "probabilidad": round(model_p * 100, 1),
                        "cuota": odds_str,
                        "ev": round(ev, 3),
                        "razon": razon,
                        "expected_total": round(expected_total, 1),
                        "api_odds": api_odds
                    })

        # Filtro: 1 solo pick por partido (el de mayor EV)
        picks_by_match = defaultdict(list)
        for r in resultados:
            picks_by_match[r["partido"]].append(r)
        
        best_picks = [max(picks, key=lambda x: x["ev"]) for picks in picks_by_match.values()]
        best_picks.sort(key=lambda x: x["ev"], reverse=True)
        parlay = best_picks[:5]

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

