import math
import numpy as np

def poisson_pmf(k, lam):
    if lam <= 0: return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def get_poisson_probs(lambda_home, lambda_away):
    max_goals = 8
    p_home = p_draw = p_away = 0.0
    # Matriz para cálculos rápidos
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

    def build_parlay(self, games):
        resultados = []
        for g in games:
            # Limpieza de nombres
            h_name = g.get('home', 'Local')
            v_name = g.get('away', 'Visita')
            partido = f"{h_name} vs {v_name}"
            
            # --- AJUSTE DINÁMICO DE FUERZA (LAMBDA) ---
            # Si no hay momio, usamos base competitiva (2.8 goles totales)
            l_home, l_away = 1.5, 1.3 
            
            try:
                # Si el momio es muy bajo (favorito), subimos su lambda
                h_odd = float(str(g.get("home_odd", "100")).replace('+', ''))
                if h_odd < 0: l_home += 0.9
                elif h_odd < 150: l_home += 0.4
            except: pass

            ph, pd, pa = get_poisson_probs(l_home, l_away)
            
            # Probabilidades de mercados secundarios
            p_0_0 = poisson_pmf(0, l_home) * poisson_pmf(0, l_away)
            p_1_0 = poisson_pmf(1, l_home) * poisson_pmf(0, l_away)
            p_0_1 = poisson_pmf(0, l_home) * poisson_pmf(1, l_away)
            
            p_over_1_5 = 1 - (p_0_0 + p_1_0 + p_0_1)
            p_btts = (1 - poisson_pmf(0, l_home)) * (1 - poisson_pmf(0, l_away))
            p_over_2_5 = p_over_1_5 * 0.72 # Ratio estadístico

            # --- CASCADA DE DECISIÓN (Busca el pick más seguro/valioso) ---
            if p_over_1_5 >= 0.85:
                chosen = {"pick": "Over 1.5 Goles", "prob": p_over_1_5, "cuota": 1.35}
            elif ph >= 0.65:
                chosen = {"pick": f"Gana {h_name}", "prob": ph, "cuota": g.get("home_odd", 1.80)}
            elif p_btts >= 0.60:
                chosen = {"pick": "Ambos Anotan", "prob": p_btts, "cuota": 1.70}
            elif p_over_2_5 >= 0.58:
                chosen = {"pick": "Over 2.5 Goles", "prob": p_over_2_5, "cuota": 1.85}
            else:
                # Pick de seguridad: Doble Oportunidad Local
                chosen = {"pick": f"{h_name} o Empate", "prob": ph + pd, "cuota": 1.45}

            resultados.append({
                "partido": partido,
                "pick": chosen["pick"],
                "probabilidad": round(chosen["prob"] * 100, 1),
                "cuota": str(chosen["cuota"])
            })

        # Seleccionamos los 4 mejores picks para el parlay (máxima probabilidad)
        parlay = sorted(resultados, key=lambda x: x["probabilidad"], reverse=True)[:4]
        return resultados, parlay

    def simulate_parlay_profit(self, parlay, monto):
        cuota_total = 1.0
        for p in parlay:
            try:
                val = float(str(p["cuota"]).replace('+', ''))
                dec = (val/100 + 1) if val > 0 else (100/abs(val) + 1)
                cuota_total *= dec
            except: cuota_total *= 1.45 # Cuota base para picks de seguridad
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2), 
            "pago_total": round(pago, 2), 
            "ganancia_neta": round(pago - monto, 2)
        }

