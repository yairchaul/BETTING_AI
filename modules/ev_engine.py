import math
from modules.ev_scanner import calculate_ev

def poisson_pmf(k, lam):
    if lam <= 0: return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def get_poisson_probs(lambda_home, lambda_away):
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
    # Agregamos threshold=0.85 para corregir el TypeError
    def __init__(self, threshold=0.85):
        self.threshold = threshold
        self.min_ev_threshold = 0.13

    def build_parlay(self, games):
        resultados_totales = []
        for g in games:
            # Ajuste dinámico de fuerza (Lambda)
            l_home, l_away = 1.65, 1.20 
            try:
                h_odd = float(str(g.get("home_odd", "0")).replace('+', ''))
                if h_odd < 0: l_home += 0.8  
                elif h_odd < 150: l_home += 0.4
            except: pass

            ph, pd, pa = get_poisson_probs(l_home, l_away)
            
            # Probabilidades de mercados
            p_over_1_5 = 1 - (poisson_pmf(0, l_home)*poisson_pmf(0, l_away) + 
                             poisson_pmf(1, l_home)*poisson_pmf(0, l_away) + 
                             poisson_pmf(0, l_home)*poisson_pmf(1, l_away))
            
            opciones = [
                {"pick": f"{g.get('home')} o Empate", "p": ph + pd, "c": 1.25},
                {"pick": "Over 1.5 Goles", "p": p_over_1_5, "c": 1.35}
            ]

            mejor_opcion = max(opciones, key=lambda x: x['p'])

            # FORMATO FINAL EXIGIDO POR EL MAIN
            resultado = {
                "partido": f"{g.get('home', 'L')} vs {g.get('away', 'V')}",
                "pick": mejor_opcion['pick'],
                "probabilidad": round(mejor_opcion['p'] * 100, 1),
                "cuota": str(mejor_opcion['c']),
                "pasa_filtro": mejor_opcion['p'] >= self.threshold, # <--- CRÍTICO
                "ev": round(calculate_ev(mejor_opcion['p'], float(mejor_opcion['c'])), 3)
            }
            resultados_totales.append(resultado)

        # Seleccionar para el Parlay solo los que pasaron el filtro
        parlay = [r for r in resultados_totales if r["pasa_filtro"]]
        parlay = sorted(parlay, key=lambda x: x["probabilidad"], reverse=True)[:5]
        
        return resultados_totales, parlay

    def simulate_parlay_profit(self, parlay, monto):
        cuota_total = 1.0
        for p in parlay:
            try:
                val = float(str(p["cuota"]).replace('+', ''))
                dec = (val/100 + 1) if val > 0 else (100/abs(val) + 1)
                cuota_total *= dec
            except: cuota_total *= 1.30 
        
        pago = monto * cuota_total
        return {"cuota_total": round(cuota_total, 2), "pago_total": round(pago, 2), "ganancia_neta": round(pago - monto, 2)}

