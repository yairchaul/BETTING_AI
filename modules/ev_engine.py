import math
from collections import defaultdict
from modules.ev_scanner import calculate_ev # Asegúrate de que esta ruta exista

def poisson_pmf(k, lam):
    if lam <= 0: return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def get_poisson_probs(lambda_home: float, lambda_away: float):
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

    def build_parlay(self, games: list):
        resultados = []
        for g in games:
            partido = f"{g.get('home','')} vs {g.get('away','')}"
            
            # Ajuste de Lambdas según momios detectados
            l_home, l_away = 1.60, 1.15
            try:
                h_odd = float(str(g.get("home_odd", "0")).replace('+', ''))
                if h_odd < 150: l_home += 0.5 # Es muy favorito
            except: pass

            ph, pd, pa = get_poisson_probs(l_home, l_away)
            
            # --- CÁLCULO DE MERCADOS SECUNDARIOS ---
            p_over_1_5 = 0.0
            p_btts = 0.0
            for h in range(7):
                for a in range(7):
                    prob = poisson_pmf(h, l_home) * poisson_pmf(a, l_away)
                    if h + a > 1.5: p_over_1_5 += prob
                    if h > 0 and a > 0: p_btts += prob
            
            p_over_1t = p_over_1_5 * 0.45 
            p_over_2_5 = p_over_1_5 * 0.70

            # --- LÓGICA DE CASCADA REAL (Detenerse en la primera opción segura) ---
            chosen = None
            if p_over_1t >= 0.68:
                chosen = {"pick": "Over 1.5 1T", "prob": p_over_1t, "cuota": 1.85}
            elif p_btts >= 0.62:
                chosen = {"pick": "Ambos Equipos Anotan", "prob": p_btts, "cuota": 1.70}
            elif p_over_2_5 >= 0.58:
                chosen = {"pick": "Over 2.5", "prob": p_over_2_5, "cuota": 1.80}
            else:
                # Si falla la cascada, elegir al ganador más probable
                options = [(f"{g['home']} gana", ph), ("Empate", pd), (f"{g['away']} gana", pa)]
                best_o, best_p = max(options, key=lambda x: x[1])
                chosen = {"pick": best_o, "prob": best_p, "cuota": g.get("home_odd") if "gana" in best_o else 1.90}

            resultados.append({
                "partido": partido,
                "pick": chosen["pick"],
                "probabilidad": round(chosen["prob"] * 100, 1),
                "cuota": str(chosen["cuota"]),
                "ev": round(calculate_ev(chosen["prob"], float(str(chosen["cuota"]).replace('+', '')) if str(chosen["cuota"]).replace('+', '').replace('-', '').isdigit() else 1.90), 3)
            })

        # Seleccionar top 5 por probabilidad pura (seguridad)
        parlay = sorted(resultados, key=lambda x: x["probabilidad"], reverse=True)[:5]
        return resultados, parlay
